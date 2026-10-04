"""
KALATRACE Core

Subscription Priority

Defines the execution priority of event
subscriptions.
"""

from __future__ import annotations

from enum import IntEnum


class SubscriptionPriority(IntEnum):
    """
    Defines the execution order of event
    subscriptions.

    Higher values are executed first.

    Priority order (highest to lowest):

        SYSTEM
        CRITICAL
        HIGH
        NORMAL
        LOW
    """


    LOW = 10

    NORMAL = 20

    HIGH = 30

    CRITICAL = 40

    SYSTEM = 50