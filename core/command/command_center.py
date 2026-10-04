"""
KALATRACE Command Center

Central facade for command orchestration.

The CommandCenter coordinates the internal
command infrastructure:

- Command registry
- Command lifecycle management
- Command queue
- Command dispatching
- Command services

It does not execute business logic.
It provides a unified entry point for
Kernel and Orchestrator layers.
"""

from __future__ import annotations


from .command_registry import CommandRegistry

from .command_manager import CommandManager

from .command_queue import CommandQueue

from .command_dispatcher import CommandDispatcher

from .command_service import CommandService



class CommandCenter:
    """
    Main coordinator for KALATRACE commands.

    Provides a single access point to the
    command subsystem.

    Responsibilities:
    - expose command operations;
    - coordinate internal services;
    - provide operational status.

    Business execution remains delegated
    to services and executors.
    """


    def __init__(self) -> None:
        """
        Initializes command infrastructure.
        """


        self.registry = CommandRegistry()


        self.manager = CommandManager(
            self.registry
        )


        self.queue = CommandQueue()


        self.dispatcher = CommandDispatcher()


        self.service = CommandService(
            registry=self.registry,
            manager=self.manager,
            queue=self.queue,
            dispatcher=self.dispatcher,
        )


        self.initialized = True



    # =================================================
    # Lifecycle
    # =================================================


    def start(self) -> None:
        """
        Starts the Command Center.
        """

        self.initialized = True



    def stop(self) -> None:
        """
        Stops the Command Center.

        Current implementation keeps
        registered state in memory.
        """

        self.initialized = False



    def restart(self) -> None:
        """
        Restarts Command Center lifecycle.

        Keeps current in-memory state.
        """

        self.stop()

        self.start()



    @property
    def is_running(self) -> bool:
        """
        Indicates whether Command Center
        is active.
        """

        return self.initialized



    # =================================================
    # Command Operations
    # =================================================


    def create_command(
        self,
        name: str,
        objective: str,
        mission_id: str | None = None,
        priority: str = "NORMAL",
    ):
        """
        Creates a command through
        the service layer.
        """

        return self.service.create_command(
            name=name,
            objective=objective,
            mission_id=mission_id,
            priority=priority,
        )



    def enqueue_command(
        self,
        command_id: str,
    ):
        """
        Places command into queue.
        """

        return self.service.enqueue_command(
            command_id
        )



    def execute_command(
        self,
        command_id: str,
        executor: str,
    ):
        """
        Executes a command through
        dispatcher.
        """

        return self.service.execute_command(
            command_id,
            executor,
        )



    def complete_command(
        self,
        command_id: str,
    ):
        """
        Marks command as completed.
        """

        return self.service.complete_command(
            command_id
        )



    def fail_command(
        self,
        command_id: str,
    ):
        """
        Marks command as failed.
        """

        return self.service.fail_command(
            command_id
        )



    # =================================================
    # Queries
    # =================================================


    def get_command(
        self,
        command_id: str,
    ):
        """
        Retrieves command.
        """

        return self.service.get_command(
            command_id
        )



    def get_history(
        self,
        command_id: str,
    ):
        """
        Retrieves command history.
        """

        return self.service.get_history(
            command_id
        )



    # =================================================
    # Observability
    # =================================================


    def stats(self) -> dict:
        """
        Returns Command Center status.
        """

        return {

            "initialized":
                self.initialized,

            "commands":
                self.registry.count(),

            "queue_size":
                self.queue.size(),

            "executors":
                self.dispatcher.available_executors(),

        }



    def health_check(self) -> dict:
        """
        Returns operational health.
        """

        return {

            "command_center":
                "OK"
                if self.initialized
                else "STOPPED",

            "commands":
                self.registry.count(),

            "queue":
                self.queue.size(),

            "executors":
                len(
                    self.dispatcher.available_executors()
                ),

        }



    def __repr__(self) -> str:
        """
        Debug representation.
        """

        return (
            f"<CommandCenter "
            f"commands={self.registry.count()} "
            f"queue={self.queue.size()} "
            f"initialized={self.initialized}>"
        )