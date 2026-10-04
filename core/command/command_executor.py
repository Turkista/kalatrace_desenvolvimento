"""
KALATRACE Command Executor Contract

Defines the execution interface required
by any component capable of executing commands.
"""


from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)

from .command import (
    Command,
)



class CommandExecutor(
    ABC,
):
    """
    Abstract command execution contract.

    Any component capable of executing
    KALATRACE commands must implement
    this interface.
    """



    @abstractmethod
    def execute(
        self,
        command: Command,
    ) -> object:
        """
        Executes a command.

        Implementations define the
        execution behavior.

        Returns:
            Execution result produced
            by the executor.
        """

        ...



    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Returns executor identifier.

        Used for executor registration
        and command routing.
        """

        ...