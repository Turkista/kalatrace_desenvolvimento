"""
KALATRACE Kernel Module

Base contract for every orchestrated module.

Migrated from kernel/module/module.py as part
of ADR-001 (T1.1d) — moved alongside LifecycleManager,
which is the only consumer of this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.runtime.runtime_context import (
    RuntimeContext,
)


class KernelModule(ABC):
    """
    Abstract contract for KALATRACE modules.

    Lifecycle:

        initialize()
            |
            v
        start()
            |
            v
        stop()
            |
            v
        shutdown()
    """


    def __init__(
        self,
        name: str,
        context: RuntimeContext,
    ) -> None:

        if not name:
            raise ValueError(
                "Module name cannot be empty."
            )


        self.name = name

        self.context = context

        self.running = False

        self.initialized = False



    # =================================================
    # Lifecycle
    # =================================================


    @abstractmethod
    def initialize(
        self,
    ) -> None:
        """
        Initializes internal resources.
        """
        ...


    @abstractmethod
    def start(
        self,
    ) -> None:
        """
        Starts module execution.
        """
        ...


    @abstractmethod
    def stop(
        self,
    ) -> None:
        """
        Stops module execution.
        """
        ...


    @abstractmethod
    def shutdown(
        self,
    ) -> None:
        """
        Releases resources.
        """
        ...


    # =================================================
    # State
    # =================================================


    def is_running(
        self,
    ) -> bool:
        """
        Returns whether module is running.
        """

        return self.running



    def is_initialized(
        self,
    ) -> bool:
        """
        Returns whether module was initialized.
        """

        return self.initialized



    # =================================================
    # Representation
    # =================================================


    def __repr__(
        self,
    ) -> str:

        return (
            f"<KernelModule "
            f"name={self.name} "
            f"running={self.running}>"
        )