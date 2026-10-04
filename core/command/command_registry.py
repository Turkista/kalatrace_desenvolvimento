"""
KALATRACE Command Registry

Stores and manages operational commands
inside the Command Center.
"""

from __future__ import annotations

from .command import Command

from .command_status import (
    CommandStatus,
)


class CommandRegistry:
    """
    Registry responsible for command storage.

    Internal storage is encapsulated while
    maintaining backward compatibility.
    """

    def __init__(
        self,
    ) -> None:
        """
        Initializes registry.
        """

        self._commands: dict[
            str,
            Command,
        ] = {}



    # =================================================
    # Compatibility Access
    # =================================================

    @property
    def commands(
        self,
    ) -> dict[str, Command]:
        """
        Backward-compatible access to commands.

        Existing code using registry.commands
        continues working.
        """

        return self._commands



    # =================================================
    # Registration
    # =================================================

    def register(
        self,
        command: Command,
    ) -> None:
        """
        Registers a command.
        """


        if not isinstance(
            command,
            Command,
        ):
            raise TypeError(
                "Only Command instances can be registered."
            )


        if command.command_id in self._commands:

            raise ValueError(
                f"Command already registered: "
                f"{command.command_id}"
            )


        self._commands[
            command.command_id
        ] = command



    def remove(
        self,
        command_id: str,
    ) -> None:
        """
        Removes a command.
        """


        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        self._commands.pop(
            command_id,
            None,
        )



    # =================================================
    # Retrieval
    # =================================================

    def get(
        self,
        command_id: str,
    ) -> Command | None:
        """
        Retrieves command by id.
        """


        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        return self._commands.get(
            command_id
        )



    def exists(
        self,
        command_id: str,
    ) -> bool:
        """
        Checks command existence.
        """


        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        return command_id in self._commands



    # =================================================
    # Queries
    # =================================================

    def list_all(
        self,
    ) -> list[Command]:
        """
        Returns all commands.
        """


        return list(
            self._commands.values()
        )



    def list_by_status(
        self,
        status: CommandStatus | str,
    ) -> list[Command]:
        """
        Returns commands by status.
        """


        return [

            command

            for command
            in self._commands.values()

            if (
                command.status == status
                or command.status.value == status
            )

        ]



    def list_active(
        self,
    ) -> list[Command]:
        """
        Returns commands still running.
        """


        inactive_states = {

            CommandStatus.COMPLETED,

            CommandStatus.FAILED,

            CommandStatus.CANCELLED,

            CommandStatus.ARCHIVED,

        }


        return [

            command

            for command
            in self._commands.values()

            if command.status
            not in inactive_states

        ]



    # =================================================
    # Information
    # =================================================

    def count(
        self,
    ) -> int:
        """
        Returns total command count.
        """


        return len(
            self._commands
        )



    def stats(
        self,
    ) -> dict:
        """
        Returns registry statistics.
        """

        return {

            "total_commands":
                self.count(),

            "active_commands":
                len(
                    self.list_active()
                ),

            "registry":
                "CommandRegistry",

        }



    def to_dict(
        self,
    ) -> dict:
        """
        Exports registry state.
        """

        return {

            "commands":
                [
                    command.to_dict()
                    for command
                    in self._commands.values()
                ]

        }



    def clear(
        self,
    ) -> None:
        """
        Clears all registered commands.
        """

        self._commands.clear()