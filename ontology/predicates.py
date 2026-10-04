"""KALATRACE Ontology v0.1 - controlled predicates and basic constraints.

The module consumes the existing ``EdgeType`` and ``RelationshipType`` enums.
Only a small set of high-confidence compatibility rules is enforced at this
stage. Unknown combinations remain open for future domain ontologies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from shared.enums import EdgeType, RelationshipType, NodeType


Predicate = EdgeType | RelationshipType


@dataclass(frozen=True)
class OntologyPredicate:
    """Minimal semantic definition of a graph predicate."""

    value: Predicate
    description: str


CORE_PREDICATES: tuple[OntologyPredicate, ...] = tuple(
    OntologyPredicate(member, member.value.replace("_", " "))
    for member in (*EdgeType, *RelationshipType)
)

PREDICATE_REGISTRY: dict[str, OntologyPredicate] = {
    item.value.value: item for item in CORE_PREDICATES
}

# Only relationships for which the current documentation/code gives a clear
# enough initial meaning are constrained. All other known predicates remain
# semantically open and therefore return UNKNOWN rather than blocking flow.
COMPATIBILITY_RULES: dict[str, frozenset[tuple[NodeType, NodeType]]] = {
    EdgeType.SUPPORTS.value: frozenset(
        {
            (NodeType.EVIDENCE, NodeType.HYPOTHESIS),
            (NodeType.EVIDENCE, NodeType.IEC),
        }
    ),
    EdgeType.ANSWERS.value: frozenset(
        {
            (NodeType.QUESTION, NodeType.IEC),
        }
    ),
    EdgeType.VALIDATED_BY.value: frozenset(
        {
            (NodeType.IEC, NodeType.EVIDENCE),
            (NodeType.HYPOTHESIS, NodeType.EVIDENCE),
            (NodeType.DISCOVERY, NodeType.EVIDENCE),
            (NodeType.INSIGHT, NodeType.EVIDENCE),
        }
    ),
    EdgeType.DERIVED_FROM.value: frozenset(
        {
            (NodeType.EVIDENCE, NodeType.DOCUMENT),
            (NodeType.DISCOVERY, NodeType.HYPOTHESIS),
            (NodeType.INSIGHT, NodeType.DISCOVERY),
        }
    ),
}


def _predicate_value(predicate: str | Predicate) -> str:
    if isinstance(predicate, Enum):
        return str(predicate.value)
    return str(predicate)


def is_known_predicate(predicate: str | Predicate) -> bool:
    """Return whether a predicate belongs to the v0.1 vocabulary."""

    return _predicate_value(predicate) in PREDICATE_REGISTRY


def get_predicate(predicate: str | Predicate) -> OntologyPredicate | None:
    """Return a known predicate definition, if any."""

    return PREDICATE_REGISTRY.get(_predicate_value(predicate))


def compatibility(
    source_type: str | NodeType,
    predicate: str | Predicate,
    target_type: str | NodeType,
) -> str:
    """Return ``VALID``, ``INVALID`` or ``UNKNOWN`` for a graph relation.

    UNKNOWN is intentional: the v0.1 ontology must not over-constrain domain
    knowledge that has not yet been formally modelled.
    """

    try:
        source = NodeType(source_type)
        target = NodeType(target_type)
    except (ValueError, TypeError):
        return "UNKNOWN"

    predicate_value = _predicate_value(predicate)
    if predicate_value not in PREDICATE_REGISTRY:
        return "UNKNOWN"

    rules = COMPATIBILITY_RULES.get(predicate_value)
    if rules is None:
        return "UNKNOWN"

    return "VALID" if (source, target) in rules else "INVALID"
