"""
KALATRACE Core

Registry Manager

High-level coordination layer over the Registry.

Centralizes component registration, instantiation and
lifecycle operations so that callers (Runtime, ComponentLoader,
future Cognitive Orchestrator) do not manipulate registry
entries directly.
"""

from __future__ import annotations

from core.metadata import ComponentMetadata

from core.registry.registry import Registry
from core.registry.registry_entry import (
    ComponentType,
    RegistryEntry,
)


class RegistryManager:
    """
    Coordinates registration and lifecycle of components
    stored in the underlying Registry.
    """

    def __init__(
        self,
        registry: Registry | None = None,
    ) -> None:
        self._registry = (
            registry
            if registry is not None
            else Registry()
        )


    @property
    def registry(self) -> Registry:
        """
        Returns the underlying Registry instance.
        """

        return self._registry


    def register_component(
        self,
        metadata: ComponentMetadata,
        component_type: ComponentType,
        component_class: type,
    ) -> RegistryEntry:
        """
        Registers a new component and returns its registry entry.
        """

        entry = RegistryEntry(
            identifier=metadata.identifier,
            metadata=metadata,
            component_type=component_type,
            component_class=component_class,
        )

        self._registry.register(entry)

        return entry


    def unregister_component(
        self,
        identifier: str,
    ) -> None:
        """
        Removes a component registration and closes its
        runtime lifecycle, if any.
        """

        identifier = identifier.strip()

        if not identifier:
            raise ValueError(
                "Component identifier cannot be empty."
            )

        self._registry.unregister(identifier)


    def load_component(
        self,
        identifier: str,
        instance: object,
    ) -> None:
        """
        Associates a runtime instance with a registered component.
        """

        identifier = identifier.strip()

        if not identifier:
            raise ValueError(
                "Component identifier cannot be empty."
            )

        self._registry.register_instance(
            identifier,
            instance,
        )


    def unload_component(
        self,
        identifier: str,
    ) -> None:
        """
        Unload the runtime instance of a registered component.

        The component registration remains available in the registry
        and may be instantiated again later.
        """

        identifier = identifier.strip()

        if not identifier:
            raise ValueError(
                "Component identifier cannot be empty."
            )

        if not self.exists(identifier):
            raise KeyError(
                f"Component not found: {identifier}"
            )

        self._registry.clear_instance(
            identifier
        )


    def exists(
        self,
        identifier: str,
    ) -> bool:
        """
        Checks whether a component is registered.
        """

        return self._registry.exists(identifier)


    def get(
        self,
        identifier: str,
    ) -> RegistryEntry | None:
        """
        Retrieves a registered component entry.
        """

        return self._registry.get(identifier)
