"""
KALATRACE Core

Event Bus

Central communication mechanism between
KALATRACE components.

Implements a publish-subscribe architecture
with support for:

- Event subscriptions
- Priority ordering
- Event interception
- Safe dispatching
"""

from __future__ import annotations

from collections import defaultdict

from core.events.event import Event
from core.events.event_handler import EventHandler
from core.events.event_interceptor import EventInterceptor
from core.events.event_subscription import EventSubscription
from core.events.event_type import EventType
from core.events.subscription_priority import (
    SubscriptionPriority,
)


class EventBus:
    """
    Central event dispatcher.

    EventBus distributes immutable events between
    KALATRACE components without coupling producers
    and consumers.
    """

    def __init__(self) -> None:

        self._subscriptions: dict[
            EventType,
            list[EventSubscription],
        ] = defaultdict(list)

        self._interceptors: list[
            EventInterceptor
        ] = []

        self._initialized: bool = False


    # -------------------------------------------------
    # Lifecycle (added T1.1d — compatibility with
    # Kernel-style orchestrators that expect an
    # initialize()/shutdown() contract, migrated
    # from kernel/events/event_bus.py's EventBus)
    # -------------------------------------------------

    def initialize(self) -> None:
        """
        Marks the bus as ready. The bus itself is
        stateless besides subscriptions, so this is
        a lightweight lifecycle hook for orchestrators.
        """

        self._initialized = True


    def shutdown(self) -> None:
        """
        Clears subscriptions/interceptors and marks
        the bus as not initialized.
        """

        self.clear()

        self._initialized = False


    @property
    def is_initialized(self) -> bool:
        return self._initialized


    # -------------------------------------------------
    # Subscription management
    # -------------------------------------------------

    def subscribe(
        self,
        subscription: EventSubscription,
    ) -> EventSubscription:
        """
        Registers an event subscription.
        """

        if subscription is None:
            raise ValueError(
                "Subscription is required."
            )

        subscriptions = self._subscriptions[
            subscription.event_type
        ]

        for existing in subscriptions:

            if (
                existing.handler
                is subscription.handler
            ):
                return existing

        subscriptions.append(
            subscription
        )

        subscriptions.sort(
            key=lambda item:
                item.priority,
            reverse=True,
        )

        return subscription


    def create_subscription(
        self,
        event_type: EventType,
        handler: EventHandler,
        *,
        priority: SubscriptionPriority = (
            SubscriptionPriority.NORMAL
        ),
        once: bool = False,
    ) -> EventSubscription:
        """
        Creates and registers a subscription.
        """

        if not isinstance(
            event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be an EventType."
            )

        if handler is None:
            raise ValueError(
                "Event handler is required."
            )


        subscription = EventSubscription(
            event_type=event_type,
            handler=handler,
            priority=priority,
            once=once,
        )

        return self.subscribe(
            subscription
        )


    def unsubscribe(
        self,
        subscription: EventSubscription,
    ) -> None:
        """
        Removes an event subscription.
        """

        if subscription is None:
            return

        subscriptions = self._subscriptions.get(
            subscription.event_type
        )

        if not subscriptions:
            return

        if subscription in subscriptions:
            subscriptions.remove(
                subscription
            )

        if not subscriptions:
            del self._subscriptions[
                subscription.event_type
            ]


    # -------------------------------------------------
    # Interceptors
    # -------------------------------------------------

    def add_interceptor(
        self,
        interceptor: EventInterceptor,
    ) -> None:
        """
        Registers an event interceptor.
        """

        if interceptor is None:
            raise ValueError(
                "Interceptor is required."
            )

        if interceptor not in self._interceptors:
            self._interceptors.append(
                interceptor
            )


    def remove_interceptor(
        self,
        interceptor: EventInterceptor,
    ) -> None:
        """
        Removes an event interceptor.
        """

        if interceptor is None:
            return

        if interceptor in self._interceptors:
            self._interceptors.remove(
                interceptor
            )


    # -------------------------------------------------
    # Event dispatch
    # -------------------------------------------------

    def publish(
        self,
        event: Event,
    ) -> None:
        """
        Publishes an event.

        Events may be modified by interceptors
        or cancelled before reaching subscribers.
        """

        if not isinstance(
            event,
            Event,
        ):
            raise TypeError(
                "EventBus can only publish Event instances."
            )


        processed_event = event


        for interceptor in self._interceptors:

            try:

                processed_event = (
                    interceptor.before_publish(
                        processed_event
                    )
                )

            except Exception:

                continue


            if processed_event is None:
                return


            if not isinstance(
                processed_event,
                Event,
            ):
                raise TypeError(
                    "Interceptor must return an Event instance."
                )


        subscriptions = list(
            self._subscriptions.get(
                processed_event.event_type,
                [],
            )
        )


        for subscription in subscriptions:

            if not subscription.enabled:
                continue


            try:

                subscription.handler.handle(
                    processed_event
                )

                subscription.increment_dispatch()


            except Exception:

                continue


            if subscription.once:

                self.unsubscribe(
                    subscription
                )


        for interceptor in reversed(
            self._interceptors
        ):

            try:

                interceptor.after_publish(
                    processed_event
                )

            except Exception:

                continue


    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------

    def clear(self) -> None:
        """
        Removes all subscriptions and
        interceptors.
        """

        self._subscriptions.clear()

        self._interceptors.clear()


    def has_subscribers(
        self,
        event_type: EventType,
    ) -> bool:
        """
        Checks if an event has subscribers.
        """

        if not isinstance(
            event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be an EventType."
            )

        return bool(
            self._subscriptions.get(
                event_type
            )
        )


    def subscriber_count(
        self,
        event_type: EventType,
    ) -> int:
        """
        Returns number of subscribers.
        """

        if not isinstance(
            event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be an EventType."
            )

        return len(
            self._subscriptions.get(
                event_type,
                [],
            )
        )


    def get_subscriptions(
        self,
        event_type: EventType | None = None,
    ) -> tuple[
        EventSubscription,
        ...,
    ]:
        """
        Returns registered subscriptions.
        """

        if event_type is not None and not isinstance(
            event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be an EventType."
            )


        if event_type is None:

            result = []

            for subscriptions in (
                self._subscriptions.values()
            ):

                result.extend(
                    subscriptions
                )

            return tuple(result)


        return tuple(
            self._subscriptions.get(
                event_type,
                [],
            )
        )