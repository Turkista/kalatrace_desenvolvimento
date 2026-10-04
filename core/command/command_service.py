"""
KALATRACE Command Service

High-level service interface for
Command Center operations.
"""

from __future__ import annotations

from typing import Any

from .command import Command
from .command_manager import CommandManager
from .command_registry import CommandRegistry
from .command_queue import CommandQueue
from .command_dispatcher import CommandDispatcher
from .command_history import CommandHistory



class CommandService:
    """
    Provides high-level command operations.

    Coordinates command creation,
    execution flow and history tracking.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        manager: CommandManager,
        queue: CommandQueue,
        dispatcher: CommandDispatcher,
    ) -> None:
        """
        Initializes command service.
        """

        if not isinstance(
            registry,
            CommandRegistry,
        ):
            raise TypeError(
                "registry must be CommandRegistry."
            )


        if not isinstance(
            manager,
            CommandManager,
        ):
            raise TypeError(
                "manager must be CommandManager."
            )


        if not isinstance(
            queue,
            CommandQueue,
        ):
            raise TypeError(
                "queue must be CommandQueue."
            )


        if not isinstance(
            dispatcher,
            CommandDispatcher,
        ):
            raise TypeError(
                "dispatcher must be CommandDispatcher."
            )


        self.registry = registry

        self.manager = manager

        self.queue = queue

        self.dispatcher = dispatcher


        self.histories: dict[
            str,
            CommandHistory,
        ] = {}



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
        Creates a new command.
        """

        command = self.manager.create_command(
            name=name,
            objective=objective,
            mission_id=mission_id,
            priority=priority,
        )


        if command.command_id not in self.histories:

            history = CommandHistory(
                command.command_id
            )


            history.add_event(
                "Command created"
            )


            self.histories[
                command.command_id
            ] = history


        return command



    # =================================================
    # Queue
    # =================================================

    def enqueue_command(
        self,
        command_id: str,
    ) -> Command:
        """
        Adds command to execution queue.
        """

        command = self.manager.queue_command(
            command_id
        )


        self.queue.enqueue(
            command
        )


        self._history(
            command_id,
            "Command queued",
        )


        return command



    # =================================================
    # Execution
    # =================================================

    def execute_command(
        self,
        command_id: str,
        executor: str,
    ) -> Any:
        """
        Dispatches command execution.

        Return type remains generic until
        CommandDispatcher contract is finalized.
        """

        command = self.manager.dispatch_command(
            command_id
        )


        result = self.dispatcher.dispatch(
            command,
            executor,
        )


        self._history(
            command_id,
            "Command executed",
        )


        return result



    # =================================================
    # Completion
    # =================================================

    def complete_command(
        self,
        command_id: str,
    ) -> Command:

        command = self.manager.complete_command(
            command_id
        )


        self._history(
            command_id,
            "Command completed",
        )


        return command



    # =================================================
    # Failure
    # =================================================

    def fail_command(
        self,
        command_id: str,
    ) -> Command:

        command = self.manager.fail_command(
            command_id
        )


        self._history(
            command_id,
            "Command failed",
        )


        return command



    # =================================================
    # Queries
    # =================================================

    def get_command(
        self,
        command_id: str,
    ) -> Command | None:

        return self.registry.get(
            command_id
        )



    def get_history(
        self,
        command_id: str,
    ) -> CommandHistory | None:

        return self.histories.get(
            command_id
        )



    def list_histories(
        self,
    ) -> dict[str, CommandHistory]:

        return dict(
            self.histories
        )



    # =================================================
    # Internal
    # =================================================

    def _get_history(
        self,
        command_id: str,
    ) -> CommandHistory | None:
        """
        Retrieves command history.
        """

        return self.histories.get(
            command_id
        )



    def _history(
        self,
        command_id: str,
        event: str,
    ) -> None:
        """
        Adds history event.
        """

        history = self._get_history(
            command_id
        )


        if history:

            history.add_event(
                event
            )