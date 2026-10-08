from core.persistence.request_context import (
    clear_persistence_queue,
    get_pending_persistence_queue,
    queue_persistence_event,
    queue_persistence_transition,
    reset_persistence_context,
    set_persistence_context,
)


def test_persistence_queue_is_not_consumed_by_peek():
    token = set_persistence_context("token", "user")
    try:
        queue_persistence_event("IEC-1", "event", {"ok": True})
        queue_persistence_transition("IEC-1", "A", "B", "test")

        first_events, first_transitions = get_pending_persistence_queue()
        second_events, second_transitions = get_pending_persistence_queue()

        assert first_events == second_events
        assert first_transitions == second_transitions
        assert first_events
        assert first_transitions
    finally:
        reset_persistence_context(token)


def test_persistence_queue_is_cleared_explicitly_after_success():
    token = set_persistence_context("token", "user")
    try:
        queue_persistence_event("IEC-1", "event", {"ok": True})
        queue_persistence_transition("IEC-1", None, "SUPPORTED", "test")

        clear_persistence_queue()

        events, transitions = get_pending_persistence_queue()
        assert events == []
        assert transitions == []
    finally:
        reset_persistence_context(token)
