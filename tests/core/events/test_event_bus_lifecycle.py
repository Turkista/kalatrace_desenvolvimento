"""
KALATRACE Core Events - EventBus Lifecycle Smoke Tests

T1.1d - testa initialize()/shutdown()/is_initialized,
adicionados ao core.events.EventBus para compatibilidade
com kernel.kernel.Kernel (que espera esse contrato de
lifecycle, herdado do antigo kernel/events/event_bus.py).

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

from core.events import (
    Event,
    EventBus,
    EventHandler,
    EventSubscription,
    EventType,
    SubscriptionPriority,
)


class RecordingHandler(EventHandler):
    """Handler simples que grava os eventos recebidos, para asserts."""

    def __init__(self):
        self.received: list[Event] = []

    @property
    def supported_event_types(self):
        return {EventType.SYSTEM_STARTED}

    def handle(self, event: Event) -> None:
        self.received.append(event)


class TestEventBusLifecycle:
    def test_starts_not_initialized(self):
        bus = EventBus()
        assert bus.is_initialized is False

    def test_initialize_sets_flag(self):
        bus = EventBus()
        bus.initialize()
        assert bus.is_initialized is True

    def test_shutdown_clears_subscriptions_and_flag(self):
        bus = EventBus()
        bus.initialize()
        subscription = EventSubscription(
            event_type=EventType.SYSTEM_STARTED,
            handler=RecordingHandler(),
            priority=SubscriptionPriority.NORMAL,
        )
        bus.subscribe(subscription)
        assert bus.has_subscribers(EventType.SYSTEM_STARTED) is True

        bus.shutdown()

        assert bus.is_initialized is False
        assert bus.has_subscribers(EventType.SYSTEM_STARTED) is False
