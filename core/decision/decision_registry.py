"""
KALATRACE Decision Registry

Stores and manages decisions recorded by the
Decision Controller.
"""

from __future__ import annotations

from .decision import Decision
from .decision_status import DecisionStatus


class DecisionRegistry:
    """
    Registry responsible for decision storage.
    """

    def __init__(self) -> None:
        """
        Initializes registry.
        """

        self._decisions: dict[str, Decision] = {}

    # =================================================
    # Registration
    # =================================================

    def register(self, decision: Decision) -> None:
        """
        Registers a decision.
        """

        if not isinstance(decision, Decision):
            raise TypeError(
                "Only Decision instances can be registered."
            )

        if decision.decision_id in self._decisions:
            raise ValueError(
                f"Decision already registered: "
                f"{decision.decision_id}"
            )

        self._decisions[decision.decision_id] = decision

    def remove(self, decision_id: str) -> None:
        """
        Removes a decision.
        """

        if not isinstance(decision_id, str):
            raise TypeError(
                "decision_id must be a string."
            )

        self._decisions.pop(decision_id, None)

    # =================================================
    # Retrieval
    # =================================================

    def get(self, decision_id: str) -> Decision | None:
        """
        Retrieves decision by id.
        """

        if not isinstance(decision_id, str):
            raise TypeError(
                "decision_id must be a string."
            )

        return self._decisions.get(decision_id)

    def exists(self, decision_id: str) -> bool:
        """
        Checks decision existence.
        """

        if not isinstance(decision_id, str):
            raise TypeError(
                "decision_id must be a string."
            )

        return decision_id in self._decisions

    # =================================================
    # Queries
    # =================================================

    def list_all(self) -> list[Decision]:
        """
        Returns all decisions.
        """

        return list(self._decisions.values())

    def list_by_mission(self, mission_id: str) -> list[Decision]:
        """
        Returns decisions linked to a mission.
        """

        return [
            decision
            for decision in self._decisions.values()
            if decision.mission_id == mission_id
        ]

    def list_by_status(
        self,
        status: DecisionStatus | str,
    ) -> list[Decision]:
        """
        Returns decisions filtered by status.
        """

        return [
            decision
            for decision in self._decisions.values()
            if (
                decision.status == status
                or decision.status.value == status
            )
        ]

    # =================================================
    # Information
    # =================================================

    def count(self) -> int:
        """
        Returns total decision count.
        """

        return len(self._decisions)

    def stats(self) -> dict:
        """
        Returns registry statistics.
        """

        return {

            "total_decisions": self.count(),

            "accepted": len(
                self.list_by_status(DecisionStatus.ACCEPTED)
            ),

            "proposed": len(
                self.list_by_status(DecisionStatus.PROPOSED)
            ),

            "rejected": len(
                self.list_by_status(DecisionStatus.REJECTED)
            ),

            "registry": "DecisionRegistry",

        }

    def to_dict(self) -> dict:
        """
        Exports registry state.
        """

        return {
            "decisions": [
                decision.to_dict()
                for decision in self._decisions.values()
            ]
        }

    def clear(self) -> None:
        """
        Clears all registered decisions.
        """

        self._decisions.clear()
