"""
KALATRACE Core

Service Contract

Defines the required behavior of shared services
within the KALATRACE architecture.
"""

from __future__ import annotations

from abc import abstractmethod

from core.contracts.lifecycle_contract import (
    LifecycleContract,
)

from core.metadata.component_metadata import (
    ComponentMetadata,
)


class ServiceContract(LifecycleContract):
    """
    Contract for KALATRACE services.

    Services provide reusable infrastructure
    capabilities shared across the system.
    """


    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        Returns unique service identifier.
        """
        ...


    @property
    @abstractmethod
    def metadata(self) -> ComponentMetadata:
        """
        Returns service metadata information.
        """
        ...


    def health_check(self) -> bool:
        """
        Checks whether the service is healthy.

        Default implementation assumes the service
        is healthy.
        """

        return True


    @property
    def service_type(self) -> str:
        """
        Returns the service category.

        Default implementation.
        """

        return "generic"


    @property
    def dependencies(
        self,
    ) -> tuple[str, ...]:
        """
        Returns required service dependencies.

        Default implementation.
        """

        return ()