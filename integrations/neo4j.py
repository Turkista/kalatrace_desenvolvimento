from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    username: str
    password: str
    database: str
    enabled: bool = True
    connection_timeout_seconds: float = 15.0
    max_connection_lifetime_seconds: int = 3600

    @classmethod
    def from_env(cls) -> "Neo4jSettings":
        return cls(
            uri=os.getenv("NEO4J_URI", "").strip(),
            username=os.getenv("NEO4J_USERNAME", "").strip(),
            password=os.getenv("NEO4J_PASSWORD", ""),
            database=(
                os.getenv("NEO4J_DATABASE", "neo4j").strip()
                or "neo4j"
            ),
            enabled=(
                os.getenv("NEO4J_ENABLED", "true").strip().lower()
                not in {"0", "false", "no", "off"}
            ),
            connection_timeout_seconds=float(
                os.getenv(
                    "NEO4J_CONNECTION_TIMEOUT_SECONDS",
                    "15",
                )
            ),
            max_connection_lifetime_seconds=int(
                os.getenv(
                    "NEO4J_MAX_CONNECTION_LIFETIME_SECONDS",
                    "3600",
                )
            ),
        )

    def validate(self) -> None:
        if not self.enabled:
            return

        missing = []

        if not self.uri:
            missing.append("NEO4J_URI")

        if not self.username:
            missing.append("NEO4J_USERNAME")

        if not self.password:
            missing.append("NEO4J_PASSWORD")

        if missing:
            raise RuntimeError(
                "Neo4j is enabled but these variables are missing: "
                + ", ".join(missing)
            )


class Neo4jClient:
    """
    Cliente de integração com Neo4j Aura.

    Arquitetura:

        Knowledge Graph
            ├── KnowledgeNode
            └── KnowledgeEdge

        Camada epistemológica
            └── IEC

    IEC e KnowledgeNode são entidades distintas.
    """

    def __init__(
        self,
        settings: Optional[Neo4jSettings] = None,
    ):
        self.settings = settings or Neo4jSettings.from_env()
        self._driver = None

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    def _get_driver(self):
        self.settings.validate()

        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.settings.uri,
                auth=(
                    self.settings.username,
                    self.settings.password,
                ),
                connection_timeout=(
                    self.settings.connection_timeout_seconds
                ),
                max_connection_lifetime=(
                    self.settings.max_connection_lifetime_seconds
                ),
            )

        return self._driver

    def verify_connectivity(self) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "connected": False,
                "database": self.settings.database,
            }

        driver = self._get_driver()

        driver.verify_connectivity()

        with driver.session(
            database=self.settings.database
        ) as session:
            record = session.run(
                "RETURN 1 AS ok"
            ).single()

        return {
            "enabled": True,
            "connected": bool(
                record and record["ok"] == 1
            ),
            "database": self.settings.database,
        }

    def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if not self.enabled:
            raise RuntimeError(
                "Neo4j integration is disabled"
            )

        if not query or not query.strip():
            raise ValueError(
                "Neo4j query cannot be empty"
            )

        driver = self._get_driver()

        try:
            with driver.session(
                database=self.settings.database
            ) as session:
                result = session.run(
                    query,
                    parameters or {},
                )

                return [
                    record.data()
                    for record in result
                ]

        except (
            Neo4jError,
            ServiceUnavailable,
        ):
            raise

    def upsert_knowledge_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if not node_id:
            raise ValueError(
                "KnowledgeNode id cannot be empty"
            )

        safe_properties = properties or {}

        query = """
        MERGE (n:KnowledgeNode {id: $id})

        ON CREATE SET
            n.created_at = datetime()

        SET
            n.node_type = $node_type,
            n.label = $label,
            n.description = $description,
            n.updated_at = datetime()

        SET
            n.iec_id = $iec_id,
            n.origin = $origin

        RETURN n {.*} AS node
        """

        rows = self.execute(
            query,
            {
                "id": node_id,
                "node_type": node_type,
                "label": label,
                "description": description,
                "iec_id": str(
                    safe_properties.get(
                        "iec_id",
                        "",
                    )
                ),
                "origin": str(
                    safe_properties.get(
                        "origin",
                        "KALATRACE",
                    )
                ),
            },
        )

        return rows[0]["node"] if rows else {}

    def upsert_knowledge_edge(
        self,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if not edge_id:
            raise ValueError(
                "KnowledgeEdge id cannot be empty"
            )

        if not source_node_id:
            raise ValueError(
                "source_node_id cannot be empty"
            )

        if not target_node_id:
            raise ValueError(
                "target_node_id cannot be empty"
            )

        query = """
        MATCH (source:KnowledgeNode {id: $source_id})
        MATCH (target:KnowledgeNode {id: $target_id})
        MERGE (source)-[r:KNOWLEDGE_EDGE {id: $edge_id}]->(target)
        SET
            r.edge_type = $edge_type,
            r.properties = $properties,
            r.updated_at = datetime()
        RETURN
            source.id AS source_id,
            target.id AS target_id,
            r.id AS edge_id,
            r.edge_type AS edge_type,
            r.properties AS properties
        """

        rows = self.execute(
            query,
            {
                "edge_id": edge_id,
                "source_id": source_node_id,
                "target_id": target_node_id,
                "edge_type": edge_type,
                "properties": properties or {},
            },
        )

        return rows[0] if rows else {}

    def upsert_iec(
        self,
        iec_id: str,
        content: str,
        node_type: str = "Conhecimento",
    ) -> Dict[str, Any]:

        if not iec_id:
            raise ValueError(
                "IEC id cannot be empty"
            )

        query = """
        MERGE (i:IEC {id: $iec_id})
        SET
            i.content = $content,
            i.node_type = $node_type,
            i.updated_at = datetime()
        RETURN i {.*} AS iec
        """

        rows = self.execute(
            query,
            {
                "iec_id": iec_id,
                "content": content,
                "node_type": node_type,
            },
        )

        return rows[0]["iec"] if rows else {}

    def link_iec_to_knowledge_node(
        self,
        iec_id: str,
        knowledge_node_id: str,
    ) -> Dict[str, Any]:

        if not iec_id:
            raise ValueError(
                "IEC id cannot be empty"
            )

        if not knowledge_node_id:
            raise ValueError(
                "KnowledgeNode id cannot be empty"
            )

        query = """
        MATCH (i:IEC {id: $iec_id})
        MATCH (n:KnowledgeNode {id: $knowledge_node_id})
        MERGE (i)-[r:REPRESENTS]->(n)
        SET
            r.updated_at = datetime()
        RETURN
            i.id AS iec_id,
            n.id AS knowledge_node_id
        """

        rows = self.execute(
            query,
            {
                "iec_id": iec_id,
                "knowledge_node_id": knowledge_node_id,
            },
        )

        return rows[0] if rows else {}

    def get_graph_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas do Knowledge Graph e verifica integridade
        estrutural das relações persistidas no Neo4j.
        """
        if not self.enabled:
            return {
                "nodes": 0,
                "knowledge_nodes": 0,
                "iecs": 0,
                "edges": 0,
                "orphan_edges": 0,
                "duplicate_edge_ids": 0,
                "duplicate_node_ids": 0,
                "integrity_checked": False,
            }

        rows = self.execute(
            """
            MATCH (n)
            RETURN
                count(n) AS nodes,
                count { (n:KnowledgeNode) } AS knowledge_nodes,
                count { (n:IEC) } AS iecs
            """
        )
        edge_rows = self.execute(
            """
            MATCH ()-[r]->()
            RETURN count(r) AS edges
            """
        )
        integrity_rows = self.execute(
            """
            OPTIONAL MATCH (source)-[r:KNOWLEDGE_EDGE]->(target)
            WITH
                sum(CASE
                    WHEN source:KnowledgeNode AND target:KnowledgeNode THEN 0
                    ELSE 1
                END) AS orphan_edges,
                count(r.id) AS edge_id_count,
                count(DISTINCT r.id) AS edge_id_distinct_count
            OPTIONAL MATCH (n:KnowledgeNode)
            RETURN
                orphan_edges,
                greatest(0, edge_id_count - edge_id_distinct_count) AS duplicate_edge_ids,
                greatest(0, count(n.id) - count(DISTINCT n.id)) AS duplicate_node_ids
            """
        )

        if not rows:
            return {
                "nodes": 0,
                "knowledge_nodes": 0,
                "iecs": 0,
                "edges": 0,
                "orphan_edges": 0,
                "duplicate_edge_ids": 0,
                "duplicate_node_ids": 0,
                "integrity_checked": True,
            }

        row = rows[0]
        integrity = integrity_rows[0] if integrity_rows else {}

        return {
            "nodes": int(row.get("nodes", 0) or 0),
            "knowledge_nodes": int(row.get("knowledge_nodes", 0) or 0),
            "iecs": int(row.get("iecs", 0) or 0),
            "edges": int(edge_rows[0].get("edges", 0) or 0) if edge_rows else 0,
            "orphan_edges": int(integrity.get("orphan_edges", 0) or 0),
            "duplicate_edge_ids": int(integrity.get("duplicate_edge_ids", 0) or 0),
            "duplicate_node_ids": int(integrity.get("duplicate_node_ids", 0) or 0),
            "integrity_checked": True,
        }

    def get_graph(self) -> Dict[str, Any]:

        if not self.enabled:
            return {
                "enabled": False,
                "nodes": [],
                "edges": [],
                "representations": [],
            }

        nodes = self.execute(
            """
            MATCH (n)
            WHERE n:KnowledgeNode OR n:IEC
            RETURN
                labels(n) AS labels,
                n {.*} AS properties
            ORDER BY properties.id
            """
        )

        edges = self.execute(
            """
            MATCH (source:KnowledgeNode)
                  -[r:KNOWLEDGE_EDGE]->
                  (target:KnowledgeNode)
            RETURN
                source.id AS source_id,
                target.id AS target_id,
                r.id AS edge_id,
                r.edge_type AS edge_type,
                r.properties AS properties
            ORDER BY r.id
            """
        )

        representations = self.execute(
            """
            MATCH (i:IEC)-[r:REPRESENTS]->(n:KnowledgeNode)
            RETURN
                i.id AS iec_id,
                n.id AS knowledge_node_id,
                r.created_at AS created_at,
                r.updated_at AS updated_at
            ORDER BY i.id
            """
        )

        return {
            "enabled": True,
            "nodes": nodes,
            "edges": edges,
            "representations": representations,
        }

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None