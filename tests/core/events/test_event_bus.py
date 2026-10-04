"""
KALATRACE Core Events Smoke Tests

Fase 0 (T0.1) - rede de seguranca minima para core/events/
antes de qualquer fusao/refatoracao futura (ADR-001, Fase 1).

core/events e consumido por praticamente todo o resto do core,
entao qualquer fusao que mexa nele sem teste e arriscada.

Cobre o comportamento critico de:
- Event (imutabilidade, validacao, serializacao)
- EventSubscription (validacao, enable/disable, dispatch_count)
- EventBus (subscribe, publish, prioridade, once, unsubscribe,
  interceptors, utilitarios de consulta)

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.events import (
    Event,
    EventBus,
    EventHandler,
    EventInterceptor,
    EventPriority,
    EventSubscription,
    EventType,
    SubscriptionPriority,
)


# ---------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------


class RecordingHandler(EventHandler):
    """Handler simples que grava os eventos recebidos, para asserts."""

    def __init__(self, event_types=None):
        self._event_types = event_types or {EventType.SYSTEM_STARTED}
        self.received: list[Event] = []

    @property
    def supported_event_types(self):
        return self._event_types

    def handle(self, event: Event) -> None:
        self.received.append(event)


class RaisingHandler(EventHandler):
    """Handler que sempre falha - usado para testar isolamento de erros."""

    @property
    def supported_event_types(self):
        return {EventType.SYSTEM_STARTED}

    def handle(self, event: Event) -> None:
        raise RuntimeError("handler falhou de propósito")


class RecordingInterceptor(EventInterceptor):
    """Interceptor que registra chamadas de before/after publish."""

    def __init__(self):
        self.before_calls: list[Event] = []
        self.after_calls: list[Event] = []

    def before_publish(self, event):
        self.before_calls.append(event)
        return event

    def after_publish(self, event) -> None:
        self.after_calls.append(event)


def make_event(event_type=EventType.SYSTEM_STARTED, **kwargs) -> Event:
    kwargs.setdefault("source_id", "test-source")

    return Event(
        event_type=event_type,
        **kwargs,
    )


# ---------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------


def test_event_defaults():
    event = make_event()

    assert event.priority == EventPriority.NORMAL
    assert event.schema_version == "1.0"
    assert event.payload == {}
    assert event.metadata == {}
    assert event.event_id is not None


def test_event_is_immutable():
    event = make_event()

    with pytest.raises(Exception):
        event.source_id = "outro"  # type: ignore[misc]


def test_event_requires_valid_event_type():
    with pytest.raises(TypeError):
        Event(event_type="not-an-event-type", source_id="x")  # type: ignore[arg-type]


def test_event_requires_non_empty_source_id():
    with pytest.raises(ValueError):
        make_event(source_id="   ")


def test_event_with_metadata_preserves_immutability():
    original = make_event()
    updated = original.with_metadata(foo="bar")

    assert original.metadata == {}
    assert updated.metadata == {"foo": "bar"}
    assert updated.event_id == original.event_id


def test_event_payload_helpers():
    event = make_event(payload={"key": "value"})

    assert event.has_payload("key") is True
    assert event.has_payload("missing") is False
    assert event.get_payload("key") == "value"
    assert event.get_payload("missing", "default") == "default"


def test_event_to_dict_serializes_expected_fields():
    event = make_event(payload={"a": 1})
    data = event.to_dict()

    assert data["event_type"] == EventType.SYSTEM_STARTED.value
    assert data["source_id"] == "test-source"
    assert data["priority"] == EventPriority.NORMAL.name
    assert data["payload"] == {"a": 1}


# ---------------------------------------------------------------------
# EventSubscription
# ---------------------------------------------------------------------


def test_subscription_defaults():
    handler = RecordingHandler()
    subscription = EventSubscription(
        event_type=EventType.SYSTEM_STARTED,
        handler=handler,
    )

    assert subscription.priority == SubscriptionPriority.NORMAL
    assert subscription.enabled is True
    assert subscription.once is False
    assert subscription.dispatch_count == 0
    assert subscription.active is True


def test_subscription_enable_disable():
    subscription = EventSubscription(
        event_type=EventType.SYSTEM_STARTED,
        handler=RecordingHandler(),
    )

    subscription.disable()
    assert subscription.enabled is False
    assert subscription.active is False

    subscription.enable()
    assert subscription.enabled is True


def test_subscription_increment_and_reset_dispatch_count():
    subscription = EventSubscription(
        event_type=EventType.SYSTEM_STARTED,
        handler=RecordingHandler(),
    )

    subscription.increment_dispatch()
    subscription.increment_dispatch()
    assert subscription.dispatch_count == 2

    subscription.reset_dispatch_count()
    assert subscription.dispatch_count == 0


def test_subscription_requires_valid_handler():
    with pytest.raises(ValueError):
        EventSubscription(
            event_type=EventType.SYSTEM_STARTED,
            handler=object(),  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------
# EventBus - subscribe / publish basico
# ---------------------------------------------------------------------


def test_bus_starts_without_subscribers():
    bus = EventBus()

    assert bus.has_subscribers(EventType.SYSTEM_STARTED) is False
    assert bus.subscriber_count(EventType.SYSTEM_STARTED) == 0
    assert bus.get_subscriptions() == ()


def test_bus_create_subscription_and_publish_dispatches_to_handler():
    bus = EventBus()
    handler = RecordingHandler()

    bus.create_subscription(EventType.SYSTEM_STARTED, handler)
    event = make_event()
    bus.publish(event)

    assert handler.received == [event]
    assert bus.subscriber_count(EventType.SYSTEM_STARTED) == 1


def test_bus_publish_ignores_unrelated_event_types():
    bus = EventBus()
    handler = RecordingHandler({EventType.SYSTEM_STARTED})

    bus.create_subscription(EventType.SYSTEM_STARTED, handler)
    bus.publish(make_event(EventType.SYSTEM_STOPPED))

    assert handler.received == []


def test_bus_publish_requires_event_instance():
    bus = EventBus()

    with pytest.raises(TypeError):
        bus.publish("not-an-event")  # type: ignore[arg-type]


def test_bus_subscribing_same_handler_twice_is_idempotent():
    bus = EventBus()
    handler = RecordingHandler()

    first = bus.create_subscription(EventType.SYSTEM_STARTED, handler)
    second = bus.create_subscription(EventType.SYSTEM_STARTED, handler)

    assert first is second
    assert bus.subscriber_count(EventType.SYSTEM_STARTED) == 1


# ---------------------------------------------------------------------
# EventBus - prioridade de dispatch
# ---------------------------------------------------------------------


def test_bus_dispatches_in_priority_order_highest_first():
    bus = EventBus()
    order: list[str] = []

    class TrackingHandler(EventHandler):
        def __init__(self, name):
            self.name = name

        @property
        def supported_event_types(self):
            return {EventType.SYSTEM_STARTED}

        def handle(self, event):
            order.append(self.name)

    bus.create_subscription(
        EventType.SYSTEM_STARTED,
        TrackingHandler("low"),
        priority=SubscriptionPriority.LOW,
    )
    bus.create_subscription(
        EventType.SYSTEM_STARTED,
        TrackingHandler("system"),
        priority=SubscriptionPriority.SYSTEM,
    )
    bus.create_subscription(
        EventType.SYSTEM_STARTED,
        TrackingHandler("normal"),
        priority=SubscriptionPriority.NORMAL,
    )

    bus.publish(make_event())

    assert order == ["system", "normal", "low"]


# ---------------------------------------------------------------------
# EventBus - once / unsubscribe
# ---------------------------------------------------------------------


def test_bus_once_subscription_is_removed_after_first_dispatch():
    bus = EventBus()
    handler = RecordingHandler()

    bus.create_subscription(
        EventType.SYSTEM_STARTED,
        handler,
        once=True,
    )

    bus.publish(make_event())
    bus.publish(make_event())

    assert len(handler.received) == 1
    assert bus.has_subscribers(EventType.SYSTEM_STARTED) is False


def test_bus_unsubscribe_stops_dispatch():
    bus = EventBus()
    handler = RecordingHandler()

    subscription = bus.create_subscription(EventType.SYSTEM_STARTED, handler)
    bus.unsubscribe(subscription)

    bus.publish(make_event())

    assert handler.received == []
    assert bus.has_subscribers(EventType.SYSTEM_STARTED) is False


def test_bus_disabled_subscription_is_skipped():
    bus = EventBus()
    handler = RecordingHandler()

    subscription = bus.create_subscription(EventType.SYSTEM_STARTED, handler)
    subscription.disable()

    bus.publish(make_event())

    assert handler.received == []


def test_bus_handler_exception_does_not_break_other_subscribers():
    bus = EventBus()
    good_handler = RecordingHandler()

    bus.create_subscription(EventType.SYSTEM_STARTED, RaisingHandler())
    bus.create_subscription(EventType.SYSTEM_STARTED, good_handler)

    # Nao deve propagar a excecao do RaisingHandler.
    bus.publish(make_event())

    assert len(good_handler.received) == 1


# ---------------------------------------------------------------------
# EventBus - interceptors
# ---------------------------------------------------------------------


def test_bus_interceptor_is_called_before_and_after_publish():
    bus = EventBus()
    interceptor = RecordingInterceptor()
    handler = RecordingHandler()

    bus.add_interceptor(interceptor)
    bus.create_subscription(EventType.SYSTEM_STARTED, handler)

    event = make_event()
    bus.publish(event)

    assert interceptor.before_calls == [event]
    assert interceptor.after_calls == [event]
    assert handler.received == [event]


def test_bus_interceptor_returning_none_cancels_publication():
    bus = EventBus()
    handler = RecordingHandler()

    class CancellingInterceptor(EventInterceptor):
        def before_publish(self, event):
            return None

    bus.add_interceptor(CancellingInterceptor())
    bus.create_subscription(EventType.SYSTEM_STARTED, handler)

    bus.publish(make_event())

    assert handler.received == []


def test_bus_remove_interceptor():
    bus = EventBus()
    interceptor = RecordingInterceptor()

    bus.add_interceptor(interceptor)
    bus.remove_interceptor(interceptor)
    bus.publish(make_event())

    assert interceptor.before_calls == []


# ---------------------------------------------------------------------
# EventBus - utilitarios
# ---------------------------------------------------------------------


def test_bus_clear_removes_subscriptions_and_interceptors():
    bus = EventBus()
    bus.create_subscription(EventType.SYSTEM_STARTED, RecordingHandler())
    bus.add_interceptor(RecordingInterceptor())

    bus.clear()

    assert bus.get_subscriptions() == ()
    assert bus.has_subscribers(EventType.SYSTEM_STARTED) is False


def test_bus_get_subscriptions_filters_by_event_type():
    bus = EventBus()
    sub_started = bus.create_subscription(
        EventType.SYSTEM_STARTED, RecordingHandler()
    )
    bus.create_subscription(
        EventType.SYSTEM_STOPPED,
        RecordingHandler({EventType.SYSTEM_STOPPED}),
    )

    result = bus.get_subscriptions(EventType.SYSTEM_STARTED)

    assert result == (sub_started,)
