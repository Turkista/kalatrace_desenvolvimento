"""
KALATRACE Core Lifecycle Smoke Tests

Fase 0 (T0.2) - rede de seguranca minima para core/lifecycle/
antes da comparacao/fusao com kernel/lifecycle (ADR-001, Fase 1,
tarefa T1.1a).

Cobre o comportamento critico de:
- ComponentState (classificacao de estados, can_transition_to)
- LifecycleStateMachine (fonte de verdade das transicoes)
- Lifecycle (implementacao concreta usada pelos componentes)

Inclui tambem um teste que DOCUMENTA uma divergencia encontrada
entre ComponentState.can_transition_to() e LifecycleStateMachine:
as duas fontes de regra de transicao NAO concordam entre si hoje.
Isso e relevante para a decisao da T1.1a (qual e a versao
"superconjunto funcional" real) e nao deve ser silenciosamente
perdido numa fusao futura.

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.exceptions import InvalidStateTransition
from core.lifecycle import (
    ComponentState,
    Lifecycle,
    LifecycleStateMachine,
)


class ConcreteLifecycle(Lifecycle):
    """Implementacao minima concreta para exercitar Lifecycle (ABC)."""

    def initialize(self) -> None:
        self.set_state(ComponentState.INITIALIZED)

    def start(self) -> None:
        self.set_state(ComponentState.STARTING)
        self.set_state(ComponentState.RUNNING)

    def stop(self) -> None:
        self.set_state(ComponentState.STOPPING)
        self.set_state(ComponentState.STOPPED)


# ---------------------------------------------------------------------
# ComponentState - classificacao
# ---------------------------------------------------------------------


def test_component_state_is_active_classification():
    assert ComponentState.RUNNING.is_active is True
    assert ComponentState.STARTING.is_active is True
    assert ComponentState.PAUSED.is_active is True
    assert ComponentState.CREATED.is_active is False
    assert ComponentState.STOPPED.is_active is False


def test_component_state_is_terminal_classification():
    assert ComponentState.STOPPED.is_terminal is True
    assert ComponentState.FAILED.is_terminal is True
    assert ComponentState.DISPOSED.is_terminal is True
    assert ComponentState.RUNNING.is_terminal is False


def test_component_state_can_start_and_can_stop():
    assert ComponentState.CREATED.can_start is True
    assert ComponentState.RUNNING.can_start is False
    assert ComponentState.RUNNING.can_stop is True
    assert ComponentState.CREATED.can_stop is False


def test_component_state_can_transition_to_requires_component_state():
    with pytest.raises(TypeError):
        ComponentState.CREATED.can_transition_to("running")  # type: ignore[arg-type]


# ---------------------------------------------------------------------
# LifecycleStateMachine - fonte de verdade
# ---------------------------------------------------------------------


def test_state_machine_initial_state():
    assert LifecycleStateMachine.initial_state() == ComponentState.CREATED


def test_state_machine_allows_documented_happy_path():
    assert LifecycleStateMachine.can_transition(
        ComponentState.CREATED, ComponentState.INITIALIZED
    )
    assert LifecycleStateMachine.can_transition(
        ComponentState.INITIALIZED, ComponentState.STARTING
    )
    assert LifecycleStateMachine.can_transition(
        ComponentState.STARTING, ComponentState.RUNNING
    )
    assert LifecycleStateMachine.can_transition(
        ComponentState.RUNNING, ComponentState.STOPPING
    )
    assert LifecycleStateMachine.can_transition(
        ComponentState.STOPPING, ComponentState.STOPPED
    )


def test_state_machine_rejects_invalid_transition():
    assert (
        LifecycleStateMachine.can_transition(
            ComponentState.CREATED, ComponentState.RUNNING
        )
        is False
    )


def test_state_machine_validate_transition_raises_for_invalid():
    with pytest.raises(InvalidStateTransition):
        LifecycleStateMachine.validate_transition(
            ComponentState.CREATED, ComponentState.RUNNING
        )


def test_state_machine_disposed_is_terminal_and_has_no_way_out():
    assert LifecycleStateMachine.is_terminal(ComponentState.DISPOSED) is True
    assert LifecycleStateMachine.allowed_transitions(
        ComponentState.DISPOSED
    ) == frozenset()


def test_state_machine_failed_state_allows_recovery():
    """
    FAILED nao e um beco sem saida na LifecycleStateMachine:
    o componente pode se recuperar voltando para INITIALIZED
    ou indo para STOPPED, alem de DISPOSED.
    """

    allowed = LifecycleStateMachine.allowed_transitions(
        ComponentState.FAILED
    )

    assert ComponentState.INITIALIZED in allowed
    assert ComponentState.STOPPED in allowed
    assert ComponentState.DISPOSED in allowed


def test_state_machine_describe_returns_expected_shape():
    description = LifecycleStateMachine.describe(ComponentState.RUNNING)

    assert description["state"] == "running"
    assert description["terminal"] is False
    assert "stopping" in description["allowed_transitions"]


# ---------------------------------------------------------------------
# Divergencia ComponentState.can_transition_to vs LifecycleStateMachine
# ---------------------------------------------------------------------


def test_KNOWN_DIVERGENCE_component_state_vs_state_machine_on_failed_recovery():
    """
    ACHADO (Fase 0 / T0.2): ComponentState.can_transition_to() e
    LifecycleStateMachine discordam sobre recuperacao a partir de
    FAILED.

    - LifecycleStateMachine (usada por Lifecycle.set_state, e citada
      no proprio docstring de ComponentState.can_transition_to como
      "the authoritative transition controller") permite
      FAILED -> INITIALIZED e FAILED -> STOPPED.
    - ComponentState.can_transition_to() so permite FAILED -> DISPOSED.

    Este teste nao afirma qual das duas esta "certa" - apenas
    documenta a divergencia para que ela seja resolvida
    conscientemente na T1.1a, em vez de descoberta por acidente
    durante a fusao do Kernel.
    """

    state_machine_allows_recovery = (
        ComponentState.INITIALIZED
        in LifecycleStateMachine.allowed_transitions(ComponentState.FAILED)
    )

    component_state_allows_recovery = ComponentState.FAILED.can_transition_to(
        ComponentState.INITIALIZED
    )

    assert state_machine_allows_recovery is True
    assert component_state_allows_recovery is False
    assert state_machine_allows_recovery != component_state_allows_recovery


def test_KNOWN_DIVERGENCE_component_state_vs_state_machine_on_disposal_from_early_states():
    """
    Segunda parte do mesmo achado: LifecycleStateMachine permite
    descartar (DISPOSED) um componente ainda em CREATED ou
    INITIALIZED (cancelamento antecipado); ComponentState.can_transition_to
    nao permite nenhum dos dois.
    """

    for early_state in (ComponentState.CREATED, ComponentState.INITIALIZED):

        state_machine_allows = (
            ComponentState.DISPOSED
            in LifecycleStateMachine.allowed_transitions(early_state)
        )

        component_state_allows = early_state.can_transition_to(
            ComponentState.DISPOSED
        )

        assert state_machine_allows is True
        assert component_state_allows is False


# ---------------------------------------------------------------------
# Lifecycle (implementacao concreta)
# ---------------------------------------------------------------------


def test_lifecycle_starts_in_created_state():
    lifecycle = ConcreteLifecycle()

    assert lifecycle.state == ComponentState.CREATED
    assert lifecycle.is_running is False
    assert lifecycle.is_active is False


def test_lifecycle_happy_path_transitions():
    lifecycle = ConcreteLifecycle()

    lifecycle.initialize()
    assert lifecycle.state == ComponentState.INITIALIZED

    lifecycle.start()
    assert lifecycle.state == ComponentState.RUNNING
    assert lifecycle.is_running is True
    assert lifecycle.is_active is True

    lifecycle.stop()
    assert lifecycle.state == ComponentState.STOPPED
    assert lifecycle.is_running is False


def test_lifecycle_set_state_rejects_invalid_transition():
    lifecycle = ConcreteLifecycle()

    with pytest.raises(InvalidStateTransition):
        lifecycle.set_state(ComponentState.RUNNING)


def test_lifecycle_set_state_to_same_state_is_noop():
    lifecycle = ConcreteLifecycle()
    lifecycle.set_state(ComponentState.CREATED)

    assert lifecycle.state == ComponentState.CREATED


def test_lifecycle_set_state_requires_component_state():
    lifecycle = ConcreteLifecycle()

    with pytest.raises(TypeError):
        lifecycle.set_state("running")  # type: ignore[arg-type]


def test_lifecycle_shutdown_is_idempotent_and_reaches_disposed():
    lifecycle = ConcreteLifecycle()
    lifecycle.initialize()
    lifecycle.start()
    lifecycle.stop()

    lifecycle.shutdown()
    assert lifecycle.state == ComponentState.DISPOSED

    # Chamar de novo nao deve levantar excecao (idempotente).
    lifecycle.shutdown()
    assert lifecycle.state == ComponentState.DISPOSED


def test_lifecycle_can_transition_to_delegates_to_state_machine():
    lifecycle = ConcreteLifecycle()

    assert lifecycle.can_transition_to(ComponentState.INITIALIZED) is True
    assert lifecycle.can_transition_to(ComponentState.RUNNING) is False
