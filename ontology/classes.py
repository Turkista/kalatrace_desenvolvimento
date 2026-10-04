"""KALATRACE Ontology v0.1 - controlled domain classes.

This module deliberately reuses the existing ``shared.enums.NodeType``
vocabulary. It does not introduce a second node-type enum or change the
Knowledge Graph implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.enums import NodeType


@dataclass(frozen=True)
class OntologyClass:
    """Minimal semantic definition of a class known by the ontology."""

    node_type: NodeType
    description: str


# Initial operational vocabulary only.  Domain-specific extensions can be
# added later without changing the graph infrastructure.
CORE_CLASSES: tuple[OntologyClass, ...] = (
    OntologyClass(NodeType.IEC, "Unidade principal de conhecimento."),
    OntologyClass(NodeType.EVIDENCE, "Evidência associada a uma unidade de conhecimento."),
    OntologyClass(NodeType.HYPOTHESIS, "Hipótese ou candidato de hipótese."),
    OntologyClass(NodeType.CONCEPT, "Conceito científico ou semântico."),
    OntologyClass(NodeType.DISCOVERY, "Descoberta produzida pelo processo de conhecimento."),
    OntologyClass(NodeType.QUESTION, "Pergunta científica ou de pesquisa."),
    OntologyClass(NodeType.INSIGHT, "Insight derivado do processamento do conhecimento."),
    OntologyClass(NodeType.DOCUMENT, "Documento ou fonte documental."),
)

CLASS_REGISTRY: dict[NodeType, OntologyClass] = {
    item.node_type: item for item in CORE_CLASSES
}


def is_known_class(node_type: str | NodeType) -> bool:
    """Return whether a node type belongs to the v0.1 core ontology."""

    try:
        value = NodeType(node_type)
    except (ValueError, TypeError):
        return False
    return value in CLASS_REGISTRY


def get_class(node_type: str | NodeType) -> OntologyClass | None:
    """Return the semantic definition for a known class, if any."""

    try:
        value = NodeType(node_type)
    except (ValueError, TypeError):
        return None
    return CLASS_REGISTRY.get(value)
