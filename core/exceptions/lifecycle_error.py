"""
Lifecycle exceptions.
"""


from .kalatrace_error import KalatraceError



class LifecycleError(KalatraceError):
    """
    Base lifecycle exception.
    """

    pass