"""
KALATRACE Command Entity

Represents an operational command
generated inside a mission.

A Mission defines the strategic objective.
A Command defines an executable action.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TypedDict

from uuid import uuid4

from .command_status import CommandStatus


class CommandHistoryEntry(TypedDict):
    """
    Represents a command lifecycle history entry.
    """

    event: str
    timestamp: datetime



class Command:
    """
    Core command entity.

    Represents an instruction that must
    be processed by the Command Center.
    """

    def __init__(
        self,
        name: str,
        objective: str,
        mission_id: str | None = None,
        priority: str = "NORMAL",
    ) -> None:
        """
        Creates a command.
        """

        if not isinstance(name, str):
            raise TypeError(
                "Command name must be a string."
            )

        if not isinstance(objective, str):
            raise TypeError(
                "Command objective must be a string."
            )

        if not name.strip():
            raise ValueError(
                "Command name cannot be empty."
            )

        if not objective.strip():
            raise ValueError(
                "Command objective cannot be empty."
            )


        if mission_id is not None and not isinstance(
            mission_id,
            str,
        ):
            raise TypeError(
                "mission_id must be a string or None."
            )


        self._command_id = str(
            uuid4()
        )


        self.name = name.strip()

        self.objective = objective.strip()

        self.mission_id = mission_id


        self.priority = (
            priority.strip().upper()
            if isinstance(priority, str)
            and priority.strip()
            else "NORMAL"
        )


        self.status = CommandStatus.CREATED


        now = datetime.now(
            timezone.utc
        )


        self.created_at = now

        self.updated_at = now


        self._history: list[
            CommandHistoryEntry
        ] = []


        self.add_history(
            "Command created"
        )



    # =================================================
    # Identity
    # =================================================


    @property
    def command_id(
        self,
    ) -> str:
        """
        Returns command identifier.
        """

        return self._command_id



    # =================================================
    # History
    # =================================================


    @property
    def history(
        self,
    ) -> list[CommandHistoryEntry]:
        """
        Returns command history copy.

        Prevents external mutation
        of internal state.
        """

        return list(
            self._history
        )



    def add_history(
        self,
        event: str,
    ) -> None:
        """
        Adds command lifecycle history.
        """

        if not isinstance(event, str):
            return

        if not event.strip():
            return


        timestamp = datetime.now(
            timezone.utc
        )


        self._history.append(
            {
                "event": event.strip(),
                "timestamp": timestamp,
            }
        )


        self.updated_at = timestamp



    # =================================================
    # Status
    # =================================================


    def update_status(
        self,
        status: CommandStatus,
    ) -> None:
        """
        Updates command status.

        Transition validation is handled
        by CommandStateMachine.
        """

        if not isinstance(
            status,
            CommandStatus,
        ):
            raise TypeError(
                "status must be CommandStatus."
            )


        if status == self.status:
            return


        self.status = status


        self.add_history(
            f"Status changed to {status.value}"
        )



    # =================================================
    # Serialization
    # =================================================


    def to_dict(
        self,
    ) -> dict[str, object]:
        """
        Converts command to dictionary.
        """

        return {

            "command_id":
                self.command_id,

            "name":
                self.name,

            "objective":
                self.objective,

            "mission_id":
                self.mission_id,

            "priority":
                self.priority,

            "status":
                self.status.value,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "history":
                self.history,

        }



    # =================================================
    # Representation
    # =================================================


    def __repr__(
        self,
    ) -> str:
        """
        Returns debug representation.
        """

        return (
            f"<Command "
            f"id={self.command_id} "
            f"status={self.status.value}>"
        )