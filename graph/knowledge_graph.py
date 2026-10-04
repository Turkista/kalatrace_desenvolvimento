from __future__ import annotations

from typing import Any, Dict, Optional

from knowledge.knowledge_node import KnowledgeNode


class KnowledgeGraph:
    """Knowledge Graph em memória com separação estrutural/epistemológica.

    Compatibilidade: ``nodes`` continua expondo as entidades epistemológicas
    usadas pelos engines existentes. ``knowledge_nodes`` é o registro
    estrutural que será persistido no Neo4j/Supabase.
    """

    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.knowledge_nodes: Dict[str, KnowledgeNode] = {}
        self.edges = []

    def add_node(self, entity: Any, *, knowledge_node: Optional[KnowledgeNode] = None):
        entity_id = getattr(entity, "id", None) or getattr(entity, "node_id", None)
        if not entity_id:
            raise ValueError("Knowledge graph entities require an id")

        self.nodes[entity_id] = entity

        if knowledge_node is None:
            node_type = getattr(entity, "node_type", None) or entity.__class__.__name__
            label = getattr(entity, "label", None) or getattr(entity, "statement", None) or getattr(entity, "content", None) or str(entity_id)
            knowledge_node = KnowledgeNode(
                node_id=f"knowledge:{entity_id}",
                node_type=str(node_type),
                label=str(label)[:500],
                description=str(getattr(entity, "content", None) or label),
                properties={"entity_id": str(entity_id), "entity_type": entity.__class__.__name__},
                entity_id=str(entity_id),
                entity_type=entity.__class__.__name__,
            )

        self.knowledge_nodes[knowledge_node.node_id] = knowledge_node
        return knowledge_node

    def add_knowledge_node(self, knowledge_node: KnowledgeNode, entity: Any = None):
        self.knowledge_nodes[knowledge_node.node_id] = knowledge_node
        if entity is not None:
            entity_id = getattr(entity, "id", None) or getattr(entity, "node_id", None)
            if entity_id:
                self.nodes[entity_id] = entity
        return knowledge_node

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def get_knowledge_node(self, node_id):
        return self.knowledge_nodes.get(node_id)

    def add_edge(self, source, target, relation_type="related", weight=1.0, confidence=0.5, evidence=None):
        if evidence is None:
            evidence = []
        source_id = getattr(source, "id", None) or getattr(source, "node_id", source)
        target_id = getattr(target, "id", None) or getattr(target, "node_id", target)
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "type": relation_type,
            "weight": float(weight),
            "confidence": float(confidence),
            "evidence": evidence,
        })

    def edges_of(self, node_id):
        return [e for e in self.edges if e["source"] == node_id or e["target"] == node_id]

    def neighbors(self, node_id):
        result = set()
        for e in self.edges:
            if e["source"] == node_id:
                result.add(e["target"])
            elif e["target"] == node_id:
                result.add(e["source"])
        return [self.nodes[n] for n in result if n in self.nodes]

    def isolated_nodes(self):
        connected = set()
        for e in self.edges:
            connected.add(e["source"])
            connected.add(e["target"])
        return [self.nodes[nid] for nid in self.nodes if nid not in connected]

    def low_confidence_edges(self, threshold=0.3):
        return [e for e in self.edges if e.get("confidence", 1.0) < threshold]

    def remove_edge(self, source, target):
        source_id = getattr(source, "id", None) or getattr(source, "node_id", source)
        target_id = getattr(target, "id", None) or getattr(target, "node_id", target)
        self.edges = [e for e in self.edges if not (e["source"] == source_id and e["target"] == target_id)]

    def remove_node(self, node_id):
        self.nodes.pop(node_id, None)
        self.knowledge_nodes.pop(f"knowledge:{node_id}", None)
        self.edges = [e for e in self.edges if e["source"] != node_id and e["target"] != node_id]

    def stats(self):
        return {
            "nodes": len(self.nodes),
            "knowledge_nodes": len(self.knowledge_nodes),
            "edges": len(self.edges),
            "isolated_nodes": len(self.isolated_nodes()),
        }

    def __repr__(self):
        s = self.stats()
        return f"KnowledgeGraph(nodes={s['nodes']}, knowledge_nodes={s['knowledge_nodes']}, edges={s['edges']}, isolated={s['isolated_nodes']})"
