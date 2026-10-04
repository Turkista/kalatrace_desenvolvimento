"""
KALATRACE Core

Module Contract

Defines the required behavior of modules
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


class ModuleContract(LifecycleContract):
    """
    Contract for KALATRACE modules.

    Modules represent logical groups of capabilities,
    coordinating engines, services and resources.
    """


    @property
    @abstractmethod
    def identifier(self) -> str:
        """
        Returns unique module identifier.
        """
        ...


    @property
    @abstractmethod
    def metadata(self) -> ComponentMetadata:
        """
        Returns module metadata information.
        """
        ...


    @property
    def version(self) -> str:
        """
        Returns module version.

        Default implementation.
        """

        return "1.0.0"


    @property
    def module_type(self) -> str:
        """
        Returns the module category.

        Default implementation.
        """

        return "generic"


    @property
    def dependencies(
        self,
    ) -> tuple[str, ...]:
        """
        Returns required module dependencies.

        Default implementation.
        """

        return ()