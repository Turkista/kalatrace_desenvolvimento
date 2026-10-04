"""Minimal semantic validation adapter for KALATRACE Ontology v0.1.

This module is intentionally read-only. It does not mutate the KnowledgeGraph,
nodes, edges, confidence values, or evidence. It only produces semantic
diagnostics using the existing Ontology v0.1 vocabulary.
"""

from __future__ import annotations

from typing import Any, Iterable

from ontology.ontology import CORE_ONTOLOGY


VALID = "VALID"
INVALID = "INVALID"
UNKNOWN = "UNKNOWN"


class OntologyValidator:
    """Read-only validator for graph relations against Ontology v0.1."""

    def __init__(self, ontology=CORE_ONTOLOGY) -> None:
        self.ontology = ontology

    def validate_relation(
        self,
        source_type: str,
        predicate: str,
        target_type: str,
    ) -> dict[str, Any]:
        status = self.ontology.check_relation(
            source_type, predicate, target_type
        )
        return {
            "source_type": str(source_type),
            "predicate": str(predicate),
            "target_type": str(target_type),
            "status": status,
        }

    def validate_edge(self, edge: dict[str, Any], graph: Any) -> dict[str, Any]:
        """Validate one existing graph edge without changing it."""
        source_id = edge.get("source")
        target_id = edge.get("target")
        source = graph.get_node(source_id)
        target = graph.get_node(target_id)

        if source is None or target is None:
            status = UNKNOWN
            source_type = getattr(source, "node_type", None)
            target_type = getattr(target, "node_type", None)
        else:
            source_type = source.node_type
            target_type = target.node_type
            status = self.ontology.check_relation(
                source_type,
                edge.get("type", "related"),
                target_type,
            )

        return {
            "source": source_id,
            "predicate": edge.get("type", "related"),
            "target": target_id,
            "source_type": source_type,
            "target_type": target_type,
            "status": status,
        }

    def validate_graph(self, graph: Any) -> dict[str, Any]:
        """Return semantic diagnostics for all current graph edges."""
        diagnostics = [
            self.validate_edge(edge, graph)
            for edge in getattr(graph, "edges", [])
        ]
        counts = {VALID: 0, INVALID: 0, UNKNOWN: 0}
        for item in diagnostics:
            counts[item["status"]] += 1
        return {
            "total": len(diagnostics),
            "valid": counts[VALID],
            "invalid": counts[INVALID],
            "unknown": counts[UNKNOWN],
            "diagnostics": diagnostics,
        }
