"""
KALATRACE Command Manager

Controls command lifecycle execution
inside the Command Center.
"""

from __future__ import annotations

from .command import Command
from .command_registry import CommandRegistry
from .command_status import (
    CommandStatus,
    CommandStateMachine,
)


class CommandManager:
    """
    Coordinates command lifecycle operations.

    Responsible for:
    - creating commands;
    - validating lifecycle transitions;
    - updating command state.
    """

    def __init__(
        self,
        registry: CommandRegistry,
    ) -> None:
        """
        Initializes command manager.
        """

        if not isinstance(
            registry,
            CommandRegistry,
        ):
            raise TypeError(
                "registry must be CommandRegistry."
            )

        self.registry = registry



    # =================================================
    # Internal helpers
    # =================================================

    def _get_command(
        self,
        command_id: str,
    ) -> Command:
        """
        Retrieves a command or raises an error.
        """

        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        if not command_id.strip():
            raise ValueError(
                "command_id cannot be empty."
            )


        command = self.registry.get(
            command_id
        )


        if command is None:
            raise ValueError(
                f"Command not found: {command_id}"
            )


        return command



    # =================================================
    # Creation
    # =================================================

    def create_command(
        self,
        name: str,
        objective: str,
        mission_id: str | None = None,
        priority: str = "NORMAL",
    ) -> Command:
        """
        Creates and registers a command.
        """

        command = Command(
            name=name,
            objective=objective,
            mission_id=mission_id,
            priority=priority,
        )


        self.registry.register(
            command
        )


        return command



    # =================================================
    # Lifecycle
    # =================================================

    def change_status(
        self,
        command_id: str,
        next_status: CommandStatus,
    ) -> Command:
        """
        Changes command lifecycle state.
        """

        if not isinstance(
            next_status,
            CommandStatus,
        ):
            raise TypeError(
                "next_status must be CommandStatus."
            )


        command = self._get_command(
            command_id
        )


        new_status = CommandStateMachine.transition(
            command.status,
            next_status,
        )


        command.update_status(
            new_status
        )


        return command



    # =================================================
    # Operational Actions
    # =================================================

    def queue_command(
        self,
        command_id: str,
    ) -> Command:

        return self.change_status(
            command_id,
            CommandStatus.QUEUED,
        )



    def dispatch_command(
        self,
        command_id: str,
    ) -> Command:
        """
        Sends command to execution lifecycle.
        """

        return self.change_status(
            command_id,
            CommandStatus.EXECUTING,
        )



    def start_execution(
        self,
        command_id: str,
    ) -> Command:
        """
        Starts command execution.

        Kept as a semantic alias for compatibility.
        """

        return self.dispatch_command(
            command_id
        )



    def wait_result(
        self,
        command_id: str,
    ) -> Command:

        return self.change_status(
            command_id,
            CommandStatus.WAITING,
        )



    def complete_command(
        self,
        command_id: str,
    ) -> Command:

        return self.change_status(
            command_id,
            CommandStatus.COMPLETED,
        )



    def fail_command(
        self,
        command_id: str,
    ) -> Command:

        return self.change_status(
            command_id,
            CommandStatus.FAILED,
        )



    def cancel_command(
        self,
        command_id: str,
    ) -> Command:

        return self.change_status(
            command_id,
            CommandStatus.CANCELLED,
        )



    # =================================================
    # Queries
    # =================================================

    def get_command(
        self,
        command_id: str,
    ) -> Command | None:
        """
        Returns command.
        """

        return self.registry.get(
            command_id
        )



    def list_commands(
        self,
    ) -> list[Command]:
        """
        Returns all commands.
        """

        return self.registry.list_all()



    # =================================================
    # Observability
    # =================================================

    def stats(
        self,
    ) -> dict[str, object]:
        """
        Returns manager statistics.
        """

        return {
            "commands":
                self.registry.count(),

            "manager":
                "CommandManager",
        }



    def __repr__(
        self,
    ) -> str:
        """
        Debug representation.
        """

        return (
            f"<CommandManager "
            f"commands={self.registry.count()}>"
        )