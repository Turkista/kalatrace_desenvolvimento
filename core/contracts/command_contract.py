"""
KALATRACE Core

Command Contract

Defines the abstraction for executable commands
within the KALATRACE architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.runtime.runtime_context import (
    RuntimeContext,
)


class CommandContract(ABC):
    """
    Base contract for KALATRACE commands.

    Commands represent executable intentions
    sent to the system.
    """


    @property
    @abstractmethod
    def command_type(self) -> str:
        """
        Returns the command identifier.
        """
        ...


    @property
    def command_id(self) -> str:
        """
        Returns unique command identifier.

        Default implementation.
        """

        return self.command_type


    @property
    def parameters(
        self,
    ) -> dict[str, Any]:
        """
        Returns command parameters.
        """

        return {}


    @abstractmethod
    def validate(self) -> bool:
        """
        Validates whether the command can be executed.
        """
        ...


    @abstractmethod
    def execute(
        self,
        context: RuntimeContext,
    ) -> Any:
        """
        Executes the command within a runtime context.
        """
        ...