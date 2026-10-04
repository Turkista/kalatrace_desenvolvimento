"""
KALATRACE Decision Entity

Represents a decision made by (or on behalf of) the
Command & Mission Center.

The CMC does not simply execute -- it accompanies:
- why something was executed;
- which evidence supports it;
- what confidence backs it;
- which alternatives existed.

This entity captures exactly that: a decision is not just
an action, it is an accountable, traceable choice.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from .decision_status import DecisionStatus


class Decision:
    """
    Represents a KALATRACE decision.

    A decision records an action taken (or proposed) together
    with the reasoning, evidence, confidence, and alternatives
    considered -- the "Decision Oversight" concept of the
    Command & Mission Center.
    """

    def __init__(
        self,
        action: str,
        reason: str,
        confidence: float = 0.0,
        mission_id: str | None = None,
        evidence: list[str] | None = None,
        alternatives: list[str] | None = None,
        decision_id: str | None = None,
    ) -> None:
        """
        Creates a decision.
        """

        if not isinstance(action, str):
            raise TypeError(
                "Decision action must be a string."
            )

        if not action.strip():
            raise ValueError(
                "Decision action cannot be empty."
            )

        if not isinstance(reason, str):
            raise TypeError(
                "Decision reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Decision reason cannot be empty."
            )

        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            raise TypeError(
                "confidence must be a number."
            )

        if not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(
                "Confidence must be between 0.0 and 1.0."
            )

        if mission_id is not None and not isinstance(mission_id, str):
            raise TypeError(
                "mission_id must be a string or None."
            )

        if evidence is not None and not isinstance(evidence, list):
            raise TypeError(
                "evidence must be a list of strings."
            )

        if alternatives is not None and not isinstance(alternatives, list):
            raise TypeError(
                "alternatives must be a list of strings."
            )

        self.decision_id = (
            decision_id.strip()
            if decision_id
            else str(uuid4())
        )

        self.action = action.strip()

        self.reason = reason.strip()

        self.confidence = float(confidence)

        self.mission_id = mission_id

        self.evidence: list[str] = (
            list(evidence) if evidence else []
        )

        self.alternatives: list[str] = (
            list(alternatives) if alternatives else []
        )

        self.status = DecisionStatus.PROPOSED

        self.superseded_by: str | None = None

        now = datetime.now(UTC)

        self.created_at = now

        self.updated_at = now

        self._history: list[dict[str, Any]] = []

        self._log("Decision proposed")

    # =================================================
    # Lifecycle
    # =================================================

    def _log(self, event: str) -> None:

        self._history.append(
            {
                "event": event,
                "timestamp": datetime.now(UTC),
            }
        )

        self.updated_at = datetime.now(UTC)

    def change_status(self, next_status: DecisionStatus) -> None:
        """
        Changes decision lifecycle status.

        Transition validation is handled by the caller
        (DecisionController), this method only applies it.
        """

        if not isinstance(next_status, DecisionStatus):
            raise TypeError(
                "next_status must be DecisionStatus."
            )

        self.status = next_status

        self._log(f"Status changed to {next_status.value}")

    def accept(self) -> None:

        self.change_status(DecisionStatus.ACCEPTED)

    def reject(self) -> None:

        self.change_status(DecisionStatus.REJECTED)

    def supersede(self, by_decision_id: str) -> None:
        """
        Marks this decision as superseded by another one.
        """

        if not isinstance(by_decision_id, str) or not by_decision_id.strip():
            raise ValueError(
                "by_decision_id must be a non-empty string."
            )

        self.change_status(DecisionStatus.SUPERSEDED)

        self.superseded_by = by_decision_id.strip()

        self._log(f"Superseded by {self.superseded_by}")

    def archive(self) -> None:

        self.change_status(DecisionStatus.ARCHIVED)

    # =================================================
    # Information
    # =================================================

    @property
    def history(self) -> list[dict[str, Any]]:
        """
        Returns decision history copy.
        """

        return list(self._history)

    def to_dict(self) -> dict[str, Any]:

        return {

            "decision_id": self.decision_id,

            "action": self.action,

            "reason": self.reason,

            "confidence": self.confidence,

            "mission_id": self.mission_id,

            "evidence": self.evidence,

            "alternatives": self.alternatives,

            "status": self.status.value,

            "superseded_by": self.superseded_by,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "history": self.history,

        }

    def __repr__(self) -> str:

        return (
            f"<Decision "
            f"id={self.decision_id} "
            f"action={self.action!r} "
            f"confidence={self.confidence} "
            f"status={self.status.value}>"
        )
