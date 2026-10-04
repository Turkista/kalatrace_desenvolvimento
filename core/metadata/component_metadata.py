"""
KALATRACE Core

Component Metadata

Defines metadata information for KALATRACE components.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .metadata import Metadata
from .capability import Capability
from .dependency import Dependency


@dataclass(slots=True)
class ComponentMetadata(Metadata):
    """
    Metadata describing a KALATRACE component.
    """

    category: str = ""

    dependencies: list[Dependency] = field(
        default_factory=list
    )

    capabilities: list[Capability] = field(
        default_factory=list
    )

    author: str = ""

    license: str = ""


    def __post_init__(self) -> None:
        """
        Normalize metadata fields.
        """

        self.category = self.category.strip()
        self.author = self.author.strip()
        self.license = self.license.strip()


    def add_dependency(
        self,
        dependency: Dependency,
    ) -> None:
        """
        Adds a dependency if it does not already exist.
        """

        if dependency not in self.dependencies:
            self.dependencies.append(
                dependency
            )


    def add_capability(
        self,
        capability: Capability,
    ) -> None:
        """
        Adds a capability if it does not already exist.
        """

        if capability not in self.capabilities:
            self.capabilities.append(
                capability
            )


    def has_capability(
        self,
        capability_id: str,
    ) -> bool:
        """
        Checks whether component provides
        a capability by identifier.
        """

        return any(
            capability.identifier == capability_id
            for capability in self.capabilities
        )


    def get_capability(
        self,
        capability_id: str,
    ) -> Capability | None:
        """
        Returns capability by identifier.
        """

        for capability in self.capabilities:
            if capability.identifier == capability_id:
                return capability

        return None


    def requires_dependency(
        self,
        component_id: str,
    ) -> bool:
        """
        Checks whether component requires
        a specific dependency.
        """

        return any(
            dependency.component_id == component_id
            for dependency in self.dependencies
        )