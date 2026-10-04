"""
KALATRACE Core

Runtime Context

Defines the execution environment shared
during runtime operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from core.events import EventBus
from core.registry import Registry


@dataclass(slots=True)
class RuntimeContext:
    """
    Represents the execution context of a KALATRACE runtime.

    RuntimeContext stores shared runtime resources,
    configuration and execution state information.
    """

    runtime_id: str

    registry: Registry

    event_bus: EventBus

    environment: str = "default"

    configuration: dict[str, Any] = field(
        default_factory=dict
    )

    services: dict[str, Any] = field(
        default_factory=dict
    )

    execution_id: str | None = None

    started_at: datetime | None = None

    stopped_at: datetime | None = None

    active: bool = False


    def __post_init__(self) -> None:
        """
        Validates runtime context data.
        """

        self.runtime_id = self.runtime_id.strip()

        if not self.runtime_id:
            raise ValueError(
                "Runtime identifier cannot be empty."
            )

        self.environment = self.environment.strip()

        if not self.environment:
            raise ValueError(
                "Environment cannot be empty."
            )


    def start(self) -> None:
        """
        Starts the runtime context.
        """

        if self.active:
            return

        self.started_at = (
            datetime.now(timezone.utc)
        )

        self.stopped_at = None

        self.active = True


    def stop(self) -> None:
        """
        Stops the runtime context.
        """

        if not self.active:
            return

        self.stopped_at = (
            datetime.now(timezone.utc)
        )

        self.active = False


    def get_config(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieves a configuration value.
        """

        key = key.strip()

        if not key:
            raise ValueError(
                "Configuration key cannot be empty."
            )

        return self.configuration.get(
            key,
            default,
        )


    def set_config(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Sets a configuration value.
        """

        key = key.strip()

        if not key:
            raise ValueError(
                "Configuration key cannot be empty."
            )

        self.configuration[key] = value


    def register_service(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Registers a runtime service.
        """

        name = name.strip()

        if not name:
            raise ValueError(
                "Service name cannot be empty."
            )

        if service is None:
            raise ValueError(
                "Service cannot be None."
            )

        self.services[name] = service


    def get_service(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieves a runtime service.
        """

        name = name.strip()

        if not name:
            raise ValueError(
                "Service name cannot be empty."
            )

        return self.services.get(
            name,
            default,
        )