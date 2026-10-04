"""
KALATRACE Core

Event Subscription

Defines the relationship between an event type
and an event handler.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.events.event_handler import EventHandler
from core.events.event_type import EventType
from core.events.subscription_priority import (
    SubscriptionPriority,
)


@dataclass(slots=True)
class EventSubscription:
    """
    Represents a subscription between an event
    type and an event handler.

    A subscription controls:

    - Which events are received
    - Which handler processes them
    - Execution priority
    - Lifecycle state
    """


    event_type: EventType

    handler: EventHandler

    priority: SubscriptionPriority = (
        SubscriptionPriority.NORMAL
    )

    enabled: bool = True

    once: bool = False

    subscription_id: UUID = field(
        default_factory=uuid4
    )

    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    dispatch_count: int = 0


    def __post_init__(self) -> None:
        """
        Validates subscription consistency.
        """

        if not isinstance(
            self.event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be an EventType."
            )


        if not isinstance(
            self.handler,
            EventHandler,
        ):
            raise ValueError(
                "Event subscription requires a valid EventHandler."
            )


        if not isinstance(
            self.priority,
            SubscriptionPriority,
        ):
            raise TypeError(
                "Priority must be a SubscriptionPriority."
            )


        if self.dispatch_count < 0:
            raise ValueError(
                "Dispatch count cannot be negative."
            )


    def enable(self) -> None:
        """
        Enables this subscription.
        """

        self.enabled = True


    def disable(self) -> None:
        """
        Disables this subscription.
        """

        self.enabled = False


    def increment_dispatch(self) -> None:
        """
        Increments dispatch statistics.
        """

        self.dispatch_count += 1


    def reset_dispatch_count(self) -> None:
        """
        Resets dispatch statistics.
        """

        self.dispatch_count = 0


    @property
    def active(self) -> bool:
        """
        Indicates whether subscription is active.
        """

        return self.enabled