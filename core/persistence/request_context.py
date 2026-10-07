"""Request-scoped persistence context for authenticated KALATRACE operations."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Optional, Tuple


_persistence_context: ContextVar[Optional[Tuple[str, str]]] = ContextVar(
    "kalatrace_persistence_context",
    default=None,
)


def set_persistence_context(access_token: str, user_id: str):
    return _persistence_context.set((access_token, user_id))


def reset_persistence_context(token) -> None:
    _persistence_context.reset(token)


def get_persistence_context() -> Optional[Tuple[str, str]]:
    return _persistence_context.get()
