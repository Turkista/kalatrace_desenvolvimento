"""
KALATRACE Core

Registry Entry

Defines the runtime registration information for a component managed
by the KALATRACE Registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Type

from core.metadata import ComponentMetadata


class ComponentType(Enum):
    """
    High-level categories of registered components.
    """

    ENGINE = "engine"
    SERVICE = "service"
    MANAGER = "manager"
    REGISTRY = "registry"
    PROVIDER = "provider"
    ADAPTER = "adapter"
    PLUGIN = "plugin"
    SKILL = "skill"
    OTHER = "other"


@dataclass(slots=True)
class RegistryEntry:
    """
    Represents a runtime entry managed by the Registry.

    A RegistryEntry combines:

    - Component metadata
    - Component implementation
    - Runtime lifecycle information

    Unlike ComponentMetadata, which is immutable and descriptive,
    RegistryEntry stores the mutable runtime state of a registered
    component.
    """

    identifier: str

    metadata: ComponentMetadata

    component_type: ComponentType

    component_class: Type[object]

    instance: object | None = None

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    loaded_at: datetime | None = None

    unloaded_at: datetime | None = None

    load_count: int = 0

    active: bool = False


    def __post_init__(self) -> None:
        """
        Validates registry entry data.
        """

        self.identifier = self.identifier.strip()

        if not self.identifier:
            raise ValueError(
                "Registry entry identifier cannot be empty."
            )

        if self.metadata is None:
            raise ValueError(
                "Component metadata cannot be None."
            )

        if self.component_class is None:
            raise ValueError(
                "Component class cannot be None."
            )

        if self.identifier != self.metadata.identifier:
            raise ValueError(
                "RegistryEntry identifier must match "
                "ComponentMetadata identifier."
            )


    def activate(self) -> None:
        """
        Activates the component.
        """

        self.active = True


    def deactivate(self) -> None:
        """
        Deactivates the component.
        """

        self.active = False


    def has_instance(self) -> bool:
        """
        Returns whether a component instance exists.
        """

        return self.instance is not None


    def is_loaded(self) -> bool:
        """
        Returns whether the component is currently loaded.
        """

        return (
            self.instance is not None
            and self.loaded_at is not None
        )


    def mark_loaded(self) -> None:
        """
        Records a successful component load.
        """

        if self.instance is None:
            raise RuntimeError(
                "Cannot mark component as loaded "
                "without an instance."
            )

        self.loaded_at = datetime.now(
            timezone.utc
        )

        self.unloaded_at = None

        self.load_count += 1

        self.active = True


    def mark_unloaded(self) -> None:
        """
        Records a component unload.
        """

        self.unloaded_at = datetime.now(
            timezone.utc
        )

        self.instance = None

        self.active = False


    def clear_instance(self) -> None:
        """
        Removes the current component instance.
        """

        self.instance = None


    def reset_runtime_state(self) -> None:
        """
        Resets all mutable runtime information while preserving
        the registration metadata.
        """

        self.instance = None

        self.loaded_at = None

        self.unloaded_at = None

        self.load_count = 0

        self.active = False