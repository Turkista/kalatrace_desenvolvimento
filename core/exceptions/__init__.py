"""
KALATRACE Core Exceptions.

Public exception hierarchy for the Core layer.
"""


# =================================================
# Base Exception
# =================================================

from .kalatrace_error import (
    KalatraceError,
)



# =================================================
# Lifecycle Exceptions
# =================================================

from .lifecycle_error import (
    LifecycleError,
)


from .invalid_state_transition import (
    InvalidStateTransition,
)



# =================================================
# Public API
# =================================================

__all__ = [

    "KalatraceError",

    "LifecycleError",

    "InvalidStateTransition",

]