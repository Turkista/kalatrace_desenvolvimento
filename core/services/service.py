"""
KALATRACE Kernel Service

Base class for every Kernel service.

Examples:

- EventBus
- ServiceRegistry
- Scheduler
- Logger
- SecurityManager
- ConfigurationManager

Migrated from kernel/services/service.py as
part of ADR-001 (T1.1c) — no prior equivalent
in core/.
"""

from abc import ABC, abstractmethod


class KernelService(ABC):
    """
    Base class for Kernel services.

    Services are long-lived infrastructure
    components managed by the Kernel.

    Every service follows the same lifecycle.
    """

    def __init__(
        self,
        name: str
    ):
        """
        Initializes the service.
        """

        self.name = name

        self.initialized = False


    # =================================================
    # Lifecycle
    # =================================================

    @abstractmethod
    def initialize(
        self
    ):
        """
        Allocates service resources.

        Called during Kernel initialization.
        """
        pass


    @abstractmethod
    def shutdown(
        self
    ):
        """
        Releases service resources.

        Called during Kernel shutdown.
        """
        pass


    # =================================================
    # Information
    # =================================================

    @property
    def is_initialized(
        self
    ) -> bool:
        """
        Returns initialization state.
        """

        return self.initialized


    def __repr__(
        self
    ):
        return (
            f"<KernelService "
            f"name={self.name} "
            f"initialized={self.initialized}>"
        )