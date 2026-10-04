"""
KALATRACE Decision Status Management

Defines the lifecycle of a decision recorded by the
Decision Controller, and the valid transitions between
lifecycle states.

A Decision starts as PROPOSED (a candidate produced by
reasoning, analysis, or an engine), can be ACCEPTED (used to
drive mission or command execution), REJECTED (dismissed
without being acted upon), or later SUPERSEDED by a newer
decision that revises it in light of new evidence.
"""

from __future__ import annotations

from enum import Enum


class DecisionStatus(str, Enum):
    """
    Possible states of a decision lifecycle.
    """

    PROPOSED = "PROPOSED"

    ACCEPTED = "ACCEPTED"

    REJECTED = "REJECTED"

    SUPERSEDED = "SUPERSEDED"

    ARCHIVED = "ARCHIVED"


class DecisionStateMachine:
    """
    Controls decision lifecycle transitions.

    This class only validates lifecycle rules.
    It does not mutate Decision entities.
    """

    _VALID_TRANSITIONS = {

        DecisionStatus.PROPOSED: frozenset(
            {
                DecisionStatus.ACCEPTED,
                DecisionStatus.REJECTED,
            }
        ),

        DecisionStatus.ACCEPTED: frozenset(
            {
                DecisionStatus.SUPERSEDED,
                DecisionStatus.ARCHIVED,
            }
        ),

        DecisionStatus.REJECTED: frozenset(
            {
                DecisionStatus.ARCHIVED,
            }
        ),

        DecisionStatus.SUPERSEDED: frozenset(
            {
                DecisionStatus.ARCHIVED,
            }
        ),

        DecisionStatus.ARCHIVED: frozenset(),

    }

    @classmethod
    def can_transition(
        cls,
        current_status: DecisionStatus,
        next_status: DecisionStatus,
    ) -> bool:
        """
        Checks whether a transition is allowed.
        """

        if not isinstance(current_status, DecisionStatus):
            raise TypeError(
                "current_status must be DecisionStatus."
            )

        if not isinstance(next_status, DecisionStatus):
            raise TypeError(
                "next_status must be DecisionStatus."
            )

        return next_status in cls._VALID_TRANSITIONS.get(
            current_status,
            frozenset(),
        )

    @classmethod
    def transition(
        cls,
        current_status: DecisionStatus,
        next_status: DecisionStatus,
    ) -> DecisionStatus:
        """
        Validates and returns the next state.

        The entity remains responsible for
        applying the returned state.
        """

        if not cls.can_transition(current_status, next_status):
            raise ValueError(
                "Invalid decision transition: "
                f"{current_status.value} -> "
                f"{next_status.value}"
            )

        return next_status

    @classmethod
    def allowed_transitions(
        cls,
        status: DecisionStatus,
    ) -> frozenset[DecisionStatus]:
        """
        Returns allowed next states.
        """

        if not isinstance(status, DecisionStatus):
            raise TypeError(
                "status must be DecisionStatus."
            )

        return cls._VALID_TRANSITIONS.get(
            status,
            frozenset(),
        )
