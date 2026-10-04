"""
KALATRACE Core

Runtime

Coordinates component execution environment,
component lifecycle and runtime services.
"""

from __future__ import annotations

from enum import Enum

from core.events import (
    Event,
    EventBus,
    EventType,
)

from core.registry import (
    RegistryEntry,
    RegistryManager,
)

from core.runtime.component_loader import (
    ComponentLoader,
)

from core.runtime.runtime_context import (
    RuntimeContext,
)


class RuntimeState(Enum):
    """
    Runtime execution states.
    """

    CREATED = "created"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"


class Runtime:
    """
    Main execution environment for KALATRACE.

    Runtime coordinates:

    - Component registry
    - Component loading
    - Event communication
    - Runtime context
    - Component lifecycle orchestration
    """

    def __init__(
        self,
        runtime_id: str,
        environment: str = "default",
        registry_manager: RegistryManager | None = None,
        event_bus: EventBus | None = None,
    ) -> None:

        self.registry_manager = (
            registry_manager
            if registry_manager is not None
            else RegistryManager()
        )

        self.event_bus = (
            event_bus
            if event_bus is not None
            else EventBus()
        )

        self.context = RuntimeContext(
            runtime_id=runtime_id,
            registry=self.registry_manager.registry,
            event_bus=self.event_bus,
            environment=environment,
        )

        self.loader = ComponentLoader(
            self.context
        )

        self._state = RuntimeState.CREATED


    def start(self) -> None:
        """
        Starts the runtime.

        Does nothing if already running.
        """

        if self.running:
            return

        self.context.start()

        self._state = RuntimeState.RUNNING

        self.event_bus.publish(
            Event(
                event_type=EventType.RUNTIME_STARTED,
                source_id=self.context.runtime_id,
                payload={
                    "environment":
                        self.context.environment
                },
            )
        )


    def stop(self) -> None:
        """
        Stops the runtime.

        Future lifecycle integration point:
        component shutdown orchestration.
        """

        if not self.running:
            return

        self._state = RuntimeState.STOPPING

        self.context.stop()

        self._state = RuntimeState.STOPPED

        self.event_bus.publish(
            Event(
                event_type=EventType.RUNTIME_STOPPED,
                source_id=self.context.runtime_id,
            )
        )


    def register(
        self,
        entry: RegistryEntry,
    ) -> RegistryEntry:
        """
        Registers a component.
        """

        return (
            self.registry_manager
            .register_component(entry)
        )


    def unregister(
        self,
        identifier: str,
    ) -> None:
        """
        Removes a component registration.
        """

        self.registry_manager.unregister_component(
            identifier
        )


    def load_component(
        self,
        identifier: str,
    ) -> object:
        """
        Loads a component instance.

        Component lifecycle ownership belongs
        to ComponentLoader.
        """

        if not self.running:
            raise RuntimeError(
                "Runtime must be running before loading components."
            )

        entry = (
            self.registry_manager
            .get_component(identifier)
        )

        if entry is None:
            raise KeyError(
                f"Component not found: {identifier}"
            )

        return self.loader.load(
            entry
        )


    def unload_component(
        self,
        identifier: str,
    ) -> None:
        """
        Unloads a component instance.

        Component lifecycle ownership belongs
        to ComponentLoader.
        """

        entry = (
            self.registry_manager
            .get_component(identifier)
        )

        if entry is None:
            raise KeyError(
                f"Component not found: {identifier}"
            )

        self.loader.unload(
            entry
        )

        self.event_bus.publish(
            Event(
                event_type=EventType.COMPONENT_UNLOADED,
                source_id=self.context.runtime_id,
                payload={
                    "component":
                        identifier
                },
            )
        )


    def components(
        self,
    ) -> tuple[RegistryEntry, ...]:
        """
        Returns all registered components.
        """

        return tuple(
            self.registry_manager
            .registry
            .all()
        )


    @property
    def running(
        self,
    ) -> bool:
        """
        Indicates whether runtime is active.
        """

        return (
            self._state == RuntimeState.RUNNING
        )


    @property
    def state(
        self,
    ) -> RuntimeState:
        """
        Returns current runtime state.
        """

        return self._state


    @property
    def context_active(
        self,
    ) -> bool:
        """
        Indicates whether runtime context is active.
        """

        return self.context.active