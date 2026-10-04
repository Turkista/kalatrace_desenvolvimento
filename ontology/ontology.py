"""KALATRACE Ontology v0.1.

A small operational semantic layer over the existing graph vocabulary. It is
intentionally independent from graph storage and does not alter the current
KnowledgeGraph implementation.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.enums import NodeType

from .classes import CLASS_REGISTRY, OntologyClass, get_class, is_known_class
from .predicates import (
    PREDICATE_REGISTRY,
    OntologyPredicate,
    compatibility,
    get_predicate,
    is_known_predicate,
)


@dataclass(frozen=True)
class OntologyMetadata:
    name: str = "KALATRACE Core Ontology"
    version: str = "0.1"
    status: str = "operational"


class Ontology:
    """Read-only operational ontology registry for the current MVP stage."""

    def __init__(self) -> None:
        self.metadata = OntologyMetadata()

    @property
    def classes(self) -> dict[NodeType, OntologyClass]:
        return dict(CLASS_REGISTRY)

    @property
    def predicates(self) -> dict[str, OntologyPredicate]:
        return dict(PREDICATE_REGISTRY)

    def has_class(self, node_type: str | NodeType) -> bool:
        return is_known_class(node_type)

    def get_class(self, node_type: str | NodeType) -> OntologyClass | None:
        return get_class(node_type)

    def has_predicate(self, predicate: str) -> bool:
        return is_known_predicate(predicate)

    def get_predicate(self, predicate: str) -> OntologyPredicate | None:
        return get_predicate(predicate)

    def check_relation(
        self,
        source_type: str | NodeType,
        predicate: str,
        target_type: str | NodeType,
    ) -> str:
        return compatibility(source_type, predicate, target_type)

    def describe(self) -> dict[str, object]:
        """Return a serializable summary useful for diagnostics/tests."""

        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "status": self.metadata.status,
            "classes": sorted(item.value for item in self.classes),
            "predicates": sorted(self.predicates),
        }


CORE_ONTOLOGY = Ontology()
