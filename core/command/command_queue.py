"""
KALATRACE Command Queue

Manages pending commands waiting
for execution by the Command Center.
"""

from __future__ import annotations

from collections import deque

from .command import Command



class CommandQueue:
    """
    Operational queue for commands.

    Responsible only for pending command storage.
    Execution rules belong to higher layers.
    """



    def __init__(
        self,
    ) -> None:

        self.queue: deque[Command] = deque()



    # =================================================
    # Queue Operations
    # =================================================


    def enqueue(
        self,
        command: Command,
    ) -> None:
        """
        Adds command to queue.
        """


        if not isinstance(
            command,
            Command,
        ):

            raise TypeError(
                "Only Command instances can enter queue."
            )


        command.add_history(
            "Command added to queue"
        )


        self.queue.append(
            command
        )



    def dequeue(
        self,
    ) -> Command | None:
        """
        Removes and returns next command.
        """


        if not self.queue:

            return None


        command = self.queue.popleft()


        command.add_history(
            "Command removed from queue"
        )


        return command



    def peek(
        self,
    ) -> Command | None:
        """
        Returns next command without removing.
        """


        if not self.queue:

            return None


        return self.queue[0]



    # =================================================
    # Information
    # =================================================


    def size(
        self,
    ) -> int:
        """
        Returns queue size.
        """

        return len(
            self.queue
        )



    def is_empty(
        self,
    ) -> bool:
        """
        Checks if queue is empty.
        """

        return not bool(
            self.queue
        )



    def clear(
        self,
    ) -> None:
        """
        Clears all pending commands.
        """

        self.queue.clear()



    # =================================================
    # Queries
    # =================================================


    def list_commands(
        self,
    ) -> list[Command]:
        """
        Returns queued commands.
        """

        return list(
            self.queue
        )



    def contains(
        self,
        command_id: str,
    ) -> bool:
        """
        Checks if command exists in queue.
        """


        if not isinstance(
            command_id,
            str,
        ):

            return False


        return any(

            command.command_id == command_id

            for command
            in self.queue

        )