"""Request-scoped persistence context for authenticated KALATRACE operations."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Tuple


_persistence_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "kalatrace_persistence_context",
    default=None,
)


def set_persistence_context(access_token: str, user_id: str):
    return _persistence_context.set({
        "access_token": access_token,
        "user_id": user_id,
        "events": [],
        "transitions": [],
    })


def reset_persistence_context(token) -> None:
    _persistence_context.reset(token)


def get_persistence_context() -> Optional[Dict[str, Any]]:
    return _persistence_context.get()


def queue_persistence_event(
    iec_id: Optional[str],
    event_type: str,
    details: Dict[str, Any],
) -> None:
    context = _persistence_context.get()
    if context is not None:
        context["events"].append((iec_id, event_type, dict(details)))


def queue_persistence_transition(
    iec_id: str,
    from_state: Optional[str],
    to_state: str,
    reason: str,
) -> None:
    context = _persistence_context.get()
    if context is not None:
        context["transitions"].append(
            (iec_id, from_state, to_state, reason)
        )


def get_pending_persistence_queue() -> Tuple[List[Any], List[Any]]:
    """Return a snapshot of pending records without consuming them."""
    context = _persistence_context.get()
    if context is None:
        return [], []
    return list(context["events"]), list(context["transitions"])


def clear_persistence_queue() -> None:
    """Clear pending records only after durable persistence succeeds."""
    context = _persistence_context.get()
    if context is None:
        return
    context["events"].clear()
    context["transitions"].clear()


def drain_persistence_queue() -> Tuple[List[Any], List[Any]]:
    """Backward-compatible consume operation for callers that need it."""
    events, transitions = get_pending_persistence_queue()
    clear_persistence_queue()
    return events, transitions
