"""
KALATRACE Command Status Management

Defines command lifecycle states and
valid transitions controlled by the
Command Center.
"""

from __future__ import annotations

from enum import Enum


class CommandStatus(
    str,
    Enum,
):
    """
    Possible states of a command lifecycle.
    """

    CREATED = "CREATED"

    QUEUED = "QUEUED"

    EXECUTING = "EXECUTING"

    PAUSED = "PAUSED"

    WAITING = "WAITING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"

    ARCHIVED = "ARCHIVED"


class CommandStateMachine:
    """
    Controls command lifecycle transitions.

    This class only validates lifecycle rules.
    It does not mutate Command entities.
    """

    _VALID_TRANSITIONS = {

        CommandStatus.CREATED: frozenset(
            {
                CommandStatus.QUEUED,
                CommandStatus.EXECUTING,
                CommandStatus.FAILED,
                CommandStatus.CANCELLED,
            }
        ),

        CommandStatus.QUEUED: frozenset(
            {
                CommandStatus.EXECUTING,
                CommandStatus.CANCELLED,
                CommandStatus.FAILED,
            }
        ),

        CommandStatus.EXECUTING: frozenset(
            {
                CommandStatus.PAUSED,
                CommandStatus.WAITING,
                CommandStatus.COMPLETED,
                CommandStatus.FAILED,
                CommandStatus.CANCELLED,
            }
        ),

        CommandStatus.PAUSED: frozenset(
            {
                CommandStatus.EXECUTING,
                CommandStatus.CANCELLED,
                CommandStatus.FAILED,
            }
        ),

        CommandStatus.WAITING: frozenset(
            {
                CommandStatus.EXECUTING,
                CommandStatus.COMPLETED,
                CommandStatus.FAILED,
            }
        ),

        CommandStatus.COMPLETED: frozenset(
            {
                CommandStatus.ARCHIVED,
            }
        ),

        CommandStatus.FAILED: frozenset(
            {
                CommandStatus.ARCHIVED,
            }
        ),

        CommandStatus.CANCELLED: frozenset(
            {
                CommandStatus.ARCHIVED,
            }
        ),

        CommandStatus.ARCHIVED: frozenset(),

    }


    @classmethod
    def can_transition(
        cls,
        current_status: CommandStatus,
        next_status: CommandStatus,
    ) -> bool:
        """
        Checks whether a transition is allowed.
        """

        if not isinstance(
            current_status,
            CommandStatus,
        ):
            raise TypeError(
                "current_status must be CommandStatus."
            )


        if not isinstance(
            next_status,
            CommandStatus,
        ):
            raise TypeError(
                "next_status must be CommandStatus."
            )


        return next_status in cls._VALID_TRANSITIONS.get(
            current_status,
            frozenset(),
        )


    @classmethod
    def transition(
        cls,
        current_status: CommandStatus,
        next_status: CommandStatus,
    ) -> CommandStatus:
        """
        Validates and returns the next state.

        The entity remains responsible for
        applying the returned state.
        """

        if not cls.can_transition(
            current_status,
            next_status,
        ):
            raise ValueError(
                "Invalid command transition: "
                f"{current_status.value} -> "
                f"{next_status.value}"
            )


        return next_status


    @classmethod
    def allowed_transitions(
        cls,
        status: CommandStatus,
    ) -> frozenset[CommandStatus]:
        """
        Returns allowed next states.
        """

        if not isinstance(
            status,
            CommandStatus,
        ):
            raise TypeError(
                "status must be CommandStatus."
            )


        return cls._VALID_TRANSITIONS.get(
            status,
            frozenset(),
        )