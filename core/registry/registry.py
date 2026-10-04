"""
KALATRACE Core

Registry

Central component registry for the KALATRACE architecture.

The Registry stores registered components, manages access to their
metadata and controls runtime association between registry entries
and component instances. Used by core/runtime/ as the generic,
typed registry for pluggable components (engines, services,
managers, adapters, plugins, skills as ComponentType categories).

Relationship to the other registries in the project (investigação
REGISTRY-002, roadmap de estabilização, sessão 06/08/2026): the
project has 4 other registry implementations - core/dependency/
service_registry.py (ServiceRegistry), core/mission/
mission_registry.py (MissionRegistry), core/command/
command_registry.py (CommandRegistry) and skills/skill_registry.py
(SkillRegistry). None of them import from or are imported by this
module; each has its own consumer domain (Kernel/DI, Command &
Mission Center, Skills) and its own instance of the identical
register/get/exists/list_all/count shape, but with different
storage (typed dataclass entries here vs. plain dicts in
ServiceRegistry/SkillRegistry, isinstance-checked domain objects in
MissionRegistry/CommandRegistry) and different domain-specific
query methods (list_active by state, list_by_status). Conclusion:
not a duplication to fuse - same pattern already found for Kernel
vs. core (T1.1), validation engines (T1.4a) and Reasoning engines
(T1.3c). Recommendation left in the roadmap: if a common contract
is ever wanted, define it as a thin structural Protocol (register/
get/exists/list_all/count) rather than forcing shared inheritance,
since each registry's storage model differs for real domain
reasons.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from core.registry.registry_entry import (
    ComponentType,
    RegistryEntry,
)


class Registry:
    """
    Central registry responsible for storing and managing
    KALATRACE components.
    """

    def __init__(self) -> None:
        self._entries: dict[str, RegistryEntry] = {}


    def __contains__(
        self,
        identifier: str,
    ) -> bool:
        """
        Checks whether a component is registered.
        """

        return identifier.strip() in self._entries


    def __iter__(
        self,
    ) -> Iterator[RegistryEntry]:
        """
        Iterates through registered components.
        """

        return iter(self._entries.values())


    def __len__(
        self,
    ) -> int:
        """
        Returns the number of registered components.
        """

        return len(self._entries)


    def register(
        self,
        entry: RegistryEntry,
    ) -> None:
        """
        Registers a component entry.
        """

        identifier = entry.identifier.strip()

        if not identifier:
            raise ValueError(
                "Component identifier cannot be empty."
            )

        if entry.component_class is None:
            raise ValueError(
                "Component class is required."
            )

        if identifier in self._entries:
            raise ValueError(
                f"Component already registered: {identifier}"
            )

        entry.identifier = identifier

        self._entries[identifier] = entry


    def unregister(
        self,
        identifier: str,
    ) -> None:
        """
        Removes a component from the registry.

        The component lifecycle is safely closed before
        removing the registry entry.
        """

        identifier = identifier.strip()

        entry = self._entries.pop(
            identifier,
            None,
        )

        if entry is None:
            return

        entry.mark_unloaded()


    def get(
        self,
        identifier: str,
    ) -> RegistryEntry | None:
        """
        Retrieves a registered component entry.
        """

        return self._entries.get(
            identifier.strip()
        )


    def exists(
        self,
        identifier: str,
    ) -> bool:
        """
        Checks whether a component exists.
        """

        return identifier.strip() in self


    def register_instance(
        self,
        identifier: str,
        instance: object,
    ) -> None:
        """
        Associates a runtime instance with a registered component.

        This method centralizes the component loading lifecycle.
        """

        identifier = identifier.strip()

        if instance is None:
            raise ValueError(
                "Component instance cannot be None."
            )

        entry = self.get(identifier)

        if entry is None:
            raise KeyError(
                f"Component not registered: {identifier}"
            )

        entry.instance = instance
        entry.mark_loaded()


    def clear_instance(
        self,
        identifier: str,
    ) -> None:
        """
        Removes the runtime instance of a component
        while keeping its registration.
        """

        identifier = identifier.strip()

        entry = self.get(identifier)

        if entry is None:
            return

        entry.clear_instance()


    def all(
        self,
    ) -> Iterable[RegistryEntry]:
        """
        Returns all registered components.
        """

        return tuple(self)


    def find_by_type(
        self,
        component_type: ComponentType,
    ) -> list[RegistryEntry]:
        """
        Finds components by type.
        """

        return [
            entry
            for entry in self
            if entry.component_type is component_type
        ]


    def find_by_capability(
        self,
        capability_name: str,
    ) -> list[RegistryEntry]:
        """
        Finds components exposing a capability.
        """

        return [
            entry
            for entry in self
            if entry.metadata.has_capability(
                capability_name
            )
        ]


    def find_by_tag(
        self,
        tag: str,
    ) -> list[RegistryEntry]:
        """
        Finds components by metadata tag.
        """

        return [
            entry
            for entry in self
            if entry.metadata.has_tag(
                tag
            )
        ]


    def clear(
        self,
    ) -> None:
        """
        Removes all registered components.
        """

        for entry in self._entries.values():
            entry.mark_unloaded()

        self._entries.clear()


    def keys(
        self,
    ) -> tuple[str, ...]:
        """
        Returns all registered identifiers.
        """

        return tuple(self._entries.keys())


    def values(
        self,
    ) -> tuple[RegistryEntry, ...]:
        """
        Returns all registry entries.
        """

        return tuple(self._entries.values())


    def items(
        self,
    ) -> tuple[tuple[str, RegistryEntry], ...]:
        """
        Returns all registry items.
        """

        return tuple(self._entries.items())


    @property
    def size(
        self,
    ) -> int:
        """
        Returns the number of registered components.
        """

        return len(self)