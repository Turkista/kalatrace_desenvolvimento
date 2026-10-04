"""
KALATRACE Decision Controller

Implements the "Decision Oversight" responsibility described
for the Command & Mission Center: the CMC does not just say
"execute this". It tracks why something was executed, which
evidence supports it, what confidence backs it, and which
alternatives existed.

Example (from the CMC specification):

    Decision: Prioritize IEC-045
    Reason: 3 independent studies
            + mechanistic compatibility
            + low contradiction level
    Confidence: 0.82

This module provides a facade over decision creation,
lifecycle control (accept / reject / supersede) and querying,
mirroring the structure of core.command.CommandCenter and
core.mission.MissionManager.
"""

from __future__ import annotations

from .decision import Decision
from .decision_registry import DecisionRegistry
from .decision_status import DecisionStatus, DecisionStateMachine


class DecisionController:
    """
    Coordinates decision recording, oversight, and lifecycle.

    Business execution itself is not this class's
    responsibility -- it only records and audits the
    decisions that justify execution.
    """

    def __init__(self, registry: DecisionRegistry | None = None) -> None:
        """
        Initializes the decision controller.
        """

        if registry is not None and not isinstance(registry, DecisionRegistry):
            raise TypeError(
                "registry must be a DecisionRegistry."
            )

        self.registry = registry or DecisionRegistry()

    # =================================================
    # Internal helpers
    # =================================================

    def _get_decision(self, decision_id: str) -> Decision:

        if not isinstance(decision_id, str) or not decision_id.strip():
            raise ValueError(
                "decision_id must be a non-empty string."
            )

        decision = self.registry.get(decision_id)

        if decision is None:
            raise ValueError(
                f"Decision not found: {decision_id}"
            )

        return decision

    # =================================================
    # Recording
    # =================================================

    def record_decision(
        self,
        action: str,
        reason: str,
        confidence: float = 0.0,
        mission_id: str | None = None,
        evidence: list[str] | None = None,
        alternatives: list[str] | None = None,
    ) -> Decision:
        """
        Records a new decision as PROPOSED.
        """

        decision = Decision(
            action=action,
            reason=reason,
            confidence=confidence,
            mission_id=mission_id,
            evidence=evidence,
            alternatives=alternatives,
        )

        self.registry.register(decision)

        return decision

    # =================================================
    # Lifecycle
    # =================================================

    def accept_decision(self, decision_id: str) -> Decision:
        """
        Accepts a proposed decision, making it actionable.
        """

        decision = self._get_decision(decision_id)

        DecisionStateMachine.transition(
            decision.status,
            DecisionStatus.ACCEPTED,
        )

        decision.accept()

        return decision

    def reject_decision(self, decision_id: str) -> Decision:
        """
        Rejects a proposed decision.
        """

        decision = self._get_decision(decision_id)

        DecisionStateMachine.transition(
            decision.status,
            DecisionStatus.REJECTED,
        )

        decision.reject()

        return decision

    def supersede_decision(
        self,
        decision_id: str,
        by_decision_id: str,
    ) -> Decision:
        """
        Marks an accepted decision as superseded by a newer one.
        """

        decision = self._get_decision(decision_id)

        # ensures the superseding decision actually exists
        self._get_decision(by_decision_id)

        DecisionStateMachine.transition(
            decision.status,
            DecisionStatus.SUPERSEDED,
        )

        decision.supersede(by_decision_id)

        return decision

    def archive_decision(self, decision_id: str) -> Decision:
        """
        Archives a terminal decision.
        """

        decision = self._get_decision(decision_id)

        DecisionStateMachine.transition(
            decision.status,
            DecisionStatus.ARCHIVED,
        )

        decision.archive()

        return decision

    # =================================================
    # Confidence estimation
    # =================================================

    _CONTRADICTION_ADJUSTMENT = {

        "LOW": 0.10,

        "MEDIUM": 0.0,

        "HIGH": -0.20,

    }

    def estimate_confidence(
        self,
        evidence_count: int,
        mechanistic_compatibility: bool = False,
        contradiction_level: str = "LOW",
    ) -> float:
        """
        Produces a simple, transparent confidence estimate
        from evidence volume, mechanistic plausibility, and
        the level of contradicting evidence.

        This is a lightweight heuristic meant to give a
        starting point for the "Confidence" field of a
        Decision -- it deliberately mirrors the shape of the
        CMC specification example (3 studies + mechanistic
        compatibility + low contradiction -> ~0.8 confidence).
        It is NOT a statistical or scientific confidence
        calculation and should be reviewed/overridden by the
        responsible engine or researcher when precision matters.
        """

        if not isinstance(evidence_count, int) or evidence_count < 0:
            raise ValueError(
                "evidence_count must be a non-negative integer."
            )

        level = (
            contradiction_level.strip().upper()
            if isinstance(contradiction_level, str)
            else ""
        )

        if level not in self._CONTRADICTION_ADJUSTMENT:
            raise ValueError(
                "contradiction_level must be one of: "
                f"{sorted(self._CONTRADICTION_ADJUSTMENT)}"
            )

        base = min(evidence_count * 0.20, 0.60)

        if mechanistic_compatibility:
            base += 0.15

        base += self._CONTRADICTION_ADJUSTMENT[level]

        return round(max(0.0, min(base, 1.0)), 2)

    # =================================================
    # Queries
    # =================================================

    def get_decision(self, decision_id: str) -> Decision | None:

        return self.registry.get(decision_id)

    def list_decisions(self) -> list[Decision]:

        return self.registry.list_all()

    def list_by_mission(self, mission_id: str) -> list[Decision]:

        return self.registry.list_by_mission(mission_id)

    # =================================================
    # Observability
    # =================================================

    def stats(self) -> dict:
        """
        Returns Decision Controller status.
        """

        return self.registry.stats()

    def __repr__(self) -> str:

        return (
            f"<DecisionController "
            f"decisions={self.registry.count()}>"
        )
