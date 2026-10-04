"""
KALATRACE Knowledge Lifecycle Manager.

Controls the lifecycle of scientific knowledge objects,
including IEC creation, evidence attachment, validation,
reasoning, and knowledge maintenance.

This manager is an orchestration boundary. It delegates
storage to EvidenceStore and graph operations to the graph
implementation instead of duplicating those responsibilities.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from contracts.evidence_contract import EvidenceContract


class LifecycleManager:
    """Orchestrates the knowledge lifecycle in KALATRACE."""

    def __init__(self, graph: Any, evidence_store: Any, validator: Any, reasoner: Any) -> None:
        if graph is None:
            raise ValueError("graph is required.")
        if evidence_store is None:
            raise ValueError("evidence_store is required.")
        if validator is None:
            raise ValueError("validator is required.")
        if reasoner is None:
            raise ValueError("reasoner is required.")

        self.graph = graph
        self.evidence_store = evidence_store
        self.validator = validator
        self.reasoner = reasoner

    def create_iec(self, iec: Any) -> str:
        """Register a canonical IEC in the knowledge graph."""
        if iec is None:
            raise ValueError("iec is required.")

        validate = getattr(iec, "validate", None)
        if callable(validate):
            validate()

        if hasattr(iec, "updated_at"):
            now = datetime.now(UTC).isoformat()
            if hasattr(iec, "created_at") and not iec.created_at:
                iec.created_at = now
            iec.updated_at = now

        self.graph.add_node(iec)

        iec_id = getattr(iec, "iec_id", None)
        if iec_id is None:
            iec_id = getattr(iec, "id", None)
        if not iec_id:
            raise ValueError("IEC must expose iec_id or id.")
        return str(iec_id)

    def attach_evidence(
        self, iec_id: str, evidence_id: str, content: Any,
        reliability: float = 0.5, *, title: str | None = None,
        evidence_type: str = "observation", source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create and link an EvidenceContract to an IEC."""
        if not iec_id:
            raise ValueError("iec_id is required.")
        if not evidence_id:
            raise ValueError("evidence_id is required.")

        reliability = float(reliability)
        if not 0.0 <= reliability <= 1.0:
            raise ValueError("reliability must be between 0 and 1.")

        evidence_metadata = dict(metadata or {})
        evidence_metadata.setdefault("content", content)
        evidence_metadata.setdefault("linked_iec", [])

        evidence = EvidenceContract(
            id=evidence_id,
            title=title or f"Evidence {evidence_id}",
            description=str(content),
            evidence_type=evidence_type,
            source=source,
            confidence=reliability,
            quality_score=reliability,
            metadata=evidence_metadata,
        )

        self.evidence_store.add_evidence(evidence)
        self.evidence_store.link_to_iec(evidence_id, iec_id)

        get_node = getattr(self.graph, "get_node", None)
        if callable(get_node):
            iec_obj = get_node(iec_id)
            add_evidence = getattr(iec_obj, "add_evidence", None)
            if callable(add_evidence):
                add_evidence(evidence_id)

    def connect(self, source_id: str, target_id: str, relation_type: str = "related", weight: float = 1.0) -> None:
        """Create a relationship between two knowledge objects."""
        self.graph.add_edge(source=source_id, target=target_id, relation_type=relation_type, weight=weight)

    def validate(self, iec_id: str | None = None) -> Any:
        if iec_id is not None:
            return self.validator.validate_iec(iec_id)
        return self.validator.validate_all()

    def reason(self, iec_id: str) -> Any:
        return self.reasoner.infer_connections(iec_id)

    def status(self) -> dict[str, Any]:
        return {
            "manager": "LifecycleManager",
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
            "system_quality": self.validator.system_quality_score(),
        }

    def __repr__(self) -> str:
        return (
            f"<LifecycleManager graph={type(self.graph).__name__} "
            f"validator={type(self.validator).__name__}>"
        )
