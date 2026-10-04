"""
KALATRACE Core

Event Handler

Defines the contract for components that
consume events published through the EventBus.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.events.event import Event
from core.events.event_type import EventType


class EventHandler(ABC):
    """
    Base contract for event consumers.

    Implementations receive events from the
    EventBus and execute domain-specific logic.
    """


    @property
    @abstractmethod
    def supported_event_types(
        self,
    ) -> set[EventType]:
        """
        Returns the event types supported
        by this handler.
        """
        ...


    @abstractmethod
    def handle(
        self,
        event: Event,
    ) -> None:
        """
        Processes an event.
        """
        ...


    def supports(
        self,
        event: Event,
    ) -> bool:
        """
        Checks whether this handler
        accepts the given event.
        """

        if event is None:
            return False

        supported_types = (
            self.supported_event_types
        )

        if not isinstance(
            supported_types,
            set,
        ):
            return False

        if not supported_types:
            return False

        return (
            event.event_type
            in supported_types
        )