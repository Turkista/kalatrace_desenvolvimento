"""
KALATRACE Core

Component Loader

Responsible for creating component instances
from registry entries.
"""

from __future__ import annotations

import inspect

from core.events import (
    Event,
    EventType,
)

from core.registry import RegistryEntry

from core.runtime.runtime_context import (
    RuntimeContext,
)


class ComponentLoader:
    """
    Loads component instances from registry entries.
    """

    def __init__(
        self,
        context: RuntimeContext,
    ) -> None:
        """
        Initializes the component loader.
        """

        if context is None:
            raise ValueError(
                "Runtime context is required."
            )

        self._context = context


    def load(
        self,
        entry: RegistryEntry,
    ) -> object:
        """
        Creates a new component instance or returns
        the previously loaded instance.
        """

        self._validate_entry(
            entry
        )

        if not entry.active:
            raise RuntimeError(
                f"Component inactive: {entry.identifier}"
            )

        if entry.has_instance():
            return entry.instance

        try:

            instance = self._create_instance(
                entry
            )

            self._initialize_component(
                instance
            )

            entry.instance = instance

            entry.mark_loaded()

            self._context.event_bus.publish(
                Event(
                    event_type=(
                        EventType.COMPONENT_LOADED
                    ),
                    source_id=(
                        self._context.runtime_id
                    ),
                    payload={
                        "component_id":
                            entry.identifier,
                    },
                )
            )

            return instance


        except Exception as exc:

            self._context.event_bus.publish(
                Event(
                    event_type=(
                        EventType.COMPONENT_FAILED
                    ),
                    source_id=(
                        self._context.runtime_id
                    ),
                    payload={
                        "component_id":
                            entry.identifier,

                        "error":
                            str(exc),

                        "exception_type":
                            type(exc).__name__,
                    },
                )
            )

            raise


    def unload(
        self,
        entry: RegistryEntry,
    ) -> None:
        """
        Unloads the current component instance while
        keeping the registry entry available.
        """

        self._validate_entry(
            entry
        )

        if not entry.has_instance():
            return

        self._shutdown_component(
            entry.instance
        )

        entry.clear_instance()

        entry.mark_unloaded()


    def _create_instance(
        self,
        entry: RegistryEntry,
    ) -> object:
        """
        Creates component instance.

        Supports constructors with or without
        RuntimeContext.
        """

        constructor = (
            entry.component_class
        )

        try:

            signature = inspect.signature(
                constructor
            )

        except ValueError:

            return constructor()


        parameters = (
            signature.parameters
        )


        if not parameters:
            return constructor()


        return constructor(
            self._context
        )


    def _initialize_component(
        self,
        component: object,
    ) -> None:
        """
        Initializes component when supported.
        """

        initialize = getattr(
            component,
            "initialize",
            None,
        )

        if callable(initialize):
            initialize(
                self._context
            )


    def _shutdown_component(
        self,
        component: object | None,
    ) -> None:
        """
        Shuts down component when supported.
        """

        if component is None:
            return


        shutdown = getattr(
            component,
            "shutdown",
            None,
        )

        if callable(shutdown):
            shutdown()


    def _validate_entry(
        self,
        entry: RegistryEntry,
    ) -> None:
        """
        Validates registry entry consistency.
        """

        if entry is None:
            raise ValueError(
                "Registry entry is required."
            )

        identifier = (
            entry.identifier.strip()
        )

        if not identifier:
            raise ValueError(
                "Component identifier cannot be empty."
            )

        if entry.component_class is None:
            raise ValueError(
                "Component class is required."
            )