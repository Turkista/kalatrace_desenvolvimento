"""
KALATRACE Core Events

Public event infrastructure used for
internal communication between components.

This module exposes the official event API
for KALATRACE components.

Recommended usage:

    from core.events import Event, EventBus
"""


# ---------------------------------
# Event Core
# ---------------------------------

from .event import (
    Event,
)

from .event_type import (
    EventType,
)

from .event_priority import (
    EventPriority,
)


# ---------------------------------
# Event Consumers
# ---------------------------------

from .event_handler import (
    EventHandler,
)


# ---------------------------------
# Subscriptions
# ---------------------------------

from .subscription_priority import (
    SubscriptionPriority,
)

from .event_subscription import (
    EventSubscription,
)


# ---------------------------------
# Middleware
# ---------------------------------

from .event_interceptor import (
    EventInterceptor,
)


# ---------------------------------
# Dispatcher
# ---------------------------------

from .event_bus import (
    EventBus,
)


__all__ = [

    # Event core
    "Event",
    "EventType",
    "EventPriority",

    # Event consumers
    "EventHandler",

    # Subscriptions
    "SubscriptionPriority",
    "EventSubscription",

    # Middleware
    "EventInterceptor",

    # Dispatcher
    "EventBus",
]