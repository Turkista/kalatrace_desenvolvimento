"""
KALATRACE Knowledge Lifecycle Manager.

Controls the lifecycle of scientific knowledge objects,
including IEC creation, evidence attachment, validation,
reasoning, and knowledge maintenance.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any


class LifecycleManager:
    """
    Orchestrates the knowledge lifecycle in KALATRACE.
    """

    def __init__(
        self,
        graph: Any,
        evidence_store: Any,
        validator: Any,
        reasoner: Any,
    ) -> None:
        """
        Initializes the lifecycle manager.
        """

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

    def create_iec(
        self,
        iec: Any,
    ) -> Any:
        """
        Registers a new IEC.
        """

        iec.created_at = datetime.now(UTC)

        self.graph.add_node(
            iec
        )

        return iec.id

    def attach_evidence(
        self,
        iec_id: str,
        evidence_id: str,
        content: Any,
        reliability: float = 0.5,
    ) -> None:
        """
        Creates and links evidence to an IEC.
        """

        self.evidence_store.add_evidence(
            evidence_id=evidence_id,
            content=content,
            reliability=reliability,
        )

        self.evidence_store.link_to_iec(
            evidence_id,
            iec_id,
        )

    def connect(
        self,
        source_id: str,
        target_id: str,
        relation_type: str = "related",
        weight: float = 1.0,
    ) -> None:
        """
        Creates a relationship between two IECs.
        """

        self.graph.add_edge(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            weight=weight,
        )

    def validate(
        self,
        iec_id: str | None = None,
    ) -> Any:
        """
        Validates a specific IEC or the entire knowledge base.
        """

        if iec_id is not None:
            return self.validator.validate_iec(
                iec_id
            )

        return self.validator.validate_all()

    def reason(
        self,
        iec_id: str,
    ) -> Any:
        """
        Executes inference for a specific IEC.
        """

        return self.reasoner.infer_connections(
            iec_id
        )

    def status(
        self,
    ) -> dict[str, Any]:
        """
        Returns lifecycle manager status.
        """

        return {
            "manager": "LifecycleManager",
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
            "system_quality": (
                self.validator.system_quality_score()
            ),
        }

    def __repr__(
        self,
    ) -> str:
        """
        Returns debug representation.
        """

        return (
            f"<LifecycleManager "
            f"graph={type(self.graph).__name__} "
            f"validator={type(self.validator).__name__}>"
        )