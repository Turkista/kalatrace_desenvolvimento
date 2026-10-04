"""
KALATRACE Core

Event Interceptor

Defines middleware behavior executed during
event publishing.
"""

from __future__ import annotations

from abc import ABC

from core.events.event import Event


class EventInterceptor(ABC):
    """
    Base interceptor for event processing.

    Interceptors operate as middleware inside
    the EventBus lifecycle.

    They may:

    - Inspect events
    - Validate events
    - Transform events
    - Cancel events
    - Record processing information
    """


    def before_publish(
        self,
        event: Event,
    ) -> Event | None:
        """
        Executed before event dispatch.

        Returns:

        - Event instance: continue processing
        - None: cancel event publication
        """

        if event is None:
            raise ValueError(
                "Event is required."
            )

        return event


    def after_publish(
        self,
        event: Event,
    ) -> None:
        """
        Executed after event dispatch.

        Used for post-processing actions such as
        auditing or metrics.
        """

        if event is None:
            raise ValueError(
                "Event is required."
            )

        pass