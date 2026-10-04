"""
KALATRACE Core

Lifecycle Contract

Defines the lifecycle behavior required by executable
KALATRACE components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LifecycleContract(ABC):
    """
    Contract for executable component lifecycle.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Prepare component resources.
        """
        ...

    @abstractmethod
    def start(self) -> None:
        """
        Start component execution.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """
        Stop component execution safely.
        """
        ...

    def shutdown(self) -> None:
        """
        Release component resources.

        Optional implementation.
        """
        pass