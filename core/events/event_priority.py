"""
KALATRACE Core

Event Priority

Defines event processing priority.
"""

from enum import IntEnum


class EventPriority(IntEnum):
    """
    Priority assigned to events.

    Higher values indicate higher processing priority.

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