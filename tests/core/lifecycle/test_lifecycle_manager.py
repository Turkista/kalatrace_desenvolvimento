"""
KALATRACE Core Lifecycle - Manager/Module Smoke Tests

Fase 0 (T0.2) escreveu esta suite contra kernel/lifecycle/
para comparar com core/lifecycle/ antes da fusao (ADR-001).
T1.1d executou a fusao: LifecycleManager e KernelModule foram
migrados para core/lifecycle/ (nao existe mais em kernel/), e
este arquivo foi realocado para tests/core/lifecycle/ com os
imports atualizados. O conteudo dos testes nao mudou.

IMPORTANTE PARA O HISTORICO DA DECISAO (T1.1a/T0.2):
core.lifecycle.lifecycle_manager.LifecycleManager e
core.lifecycle.lifecycle.Lifecycle/LifecycleStateMachine NAO sao
a mesma responsabilidade, apesar do nome parecido:

- Lifecycle/LifecycleStateMachine e uma maquina de estados para
  UM componente individual.
- LifecycleManager e um COORDENADOR que gerencia varios
  KernelModule ao mesmo tempo (registrar, inicializar/iniciar/
  parar/desligar todos em ordem), delegando o estado real de cada
  modulo para os proprios metodos initialized/running do modulo.

Por isso foram migrados como capacidade nova dentro de
core/lifecycle/, e nao fundidos nas classes de estado ja
existentes.

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.lifecycle.lifecycle_manager import LifecycleManager
from core.lifecycle.kernel_module import KernelModule


class FakeModule(KernelModule):
    """KernelModule minimo para exercitar o LifecycleManager sem I/O."""

    def __init__(self, name: str, fail_on_start: bool = False):
        super().__init__(name=name, context=None)
        self.fail_on_start = fail_on_start
        self.calls: list[str] = []

    def initialize(self) -> None:
        self.calls.append("initialize")
        self.initialized = True

    def start(self) -> None:
        self.calls.append("start")
        if self.fail_on_start:
            raise RuntimeError("falha proposital ao iniciar")
        self.running = True

    def stop(self) -> None:
        self.calls.append("stop")
        self.running = False

    def shutdown(self) -> None:
        self.calls.append("shutdown")
        self.initialized = False


# ---------------------------------------------------------------------
# Registro de modulos
# ---------------------------------------------------------------------


def test_manager_starts_empty():
    manager = LifecycleManager()

    assert manager.module_count() == 0
    assert manager.list_modules() == []
    assert manager.initialized is False


def test_manager_register_and_get_module():
    manager = LifecycleManager()
    module = FakeModule("alpha")

    manager.register_module(module)

    assert manager.module_count() == 1
    assert manager.has_module("alpha") is True
    assert manager.get_module("alpha") is module


def test_manager_register_duplicate_name_raises():
    manager = LifecycleManager()
    manager.register_module(FakeModule("alpha"))

    with pytest.raises(ValueError):
        manager.register_module(FakeModule("alpha"))


def test_manager_unregister_module():
    manager = LifecycleManager()
    manager.register_module(FakeModule("alpha"))

    manager.unregister_module("alpha")

    assert manager.has_module("alpha") is False
    assert manager.get_module("alpha") is None


def test_manager_unregister_unknown_module_is_noop():
    manager = LifecycleManager()

    # Nao deve levantar excecao.
    manager.unregister_module("nao-existe")


# ---------------------------------------------------------------------
# Ciclo de vida coordenado
# ---------------------------------------------------------------------


def test_manager_initialize_all_marks_manager_initialized():
    manager = LifecycleManager()
    module = FakeModule("alpha")
    manager.register_module(module)

    manager.initialize_all()

    assert manager.initialized is True
    assert module.initialized is True
    assert module.calls == ["initialize"]


def test_manager_initialize_all_skips_already_initialized_modules():
    manager = LifecycleManager()
    module = FakeModule("alpha")
    module.initialized = True
    manager.register_module(module)

    manager.initialize_all()

    assert module.calls == []


def test_manager_start_all_requires_initialize_first():
    manager = LifecycleManager()
    manager.register_module(FakeModule("alpha"))

    with pytest.raises(RuntimeError):
        manager.start_all()


def test_manager_start_all_starts_initialized_modules():
    manager = LifecycleManager()
    module = FakeModule("alpha")
    manager.register_module(module)
    manager.initialize_all()

    manager.start_all()

    assert module.running is True
    assert module.calls == ["initialize", "start"]


def test_manager_stop_all_stops_running_modules_in_reverse_order():
    manager = LifecycleManager()
    order: list[str] = []

    first = FakeModule("first")
    second = FakeModule("second")

    for module in (first, second):
        original_stop = module.stop

        def make_tracked_stop(name, original):
            def tracked_stop():
                order.append(name)
                original()
            return tracked_stop

        module.stop = make_tracked_stop(module.name, original_stop)
        manager.register_module(module)

    manager.initialize_all()
    manager.start_all()
    manager.stop_all()

    assert order == ["second", "first"]
    assert first.running is False
    assert second.running is False


def test_manager_shutdown_all_disposes_modules_and_resets_initialized_flag():
    manager = LifecycleManager()
    module = FakeModule("alpha")
    manager.register_module(module)
    manager.initialize_all()
    manager.start_all()
    manager.stop_all()

    manager.shutdown_all()

    assert module.initialized is False
    assert manager.initialized is False
    assert module.calls[-1] == "shutdown"


def test_manager_clear_removes_all_modules_without_shutting_them_down():
    manager = LifecycleManager()
    module = FakeModule("alpha")
    manager.register_module(module)

    manager.clear()

    assert manager.module_count() == 0
    assert "shutdown" not in module.calls


# ---------------------------------------------------------------------
# KernelModule (contrato usado pelo LifecycleManager)
# ---------------------------------------------------------------------


def test_kernel_module_requires_non_empty_name():
    with pytest.raises(ValueError):
        FakeModule("")


def test_kernel_module_reports_state_via_helper_methods():
    module = FakeModule("alpha")

    assert module.is_initialized() is False
    assert module.is_running() is False

    module.initialize()
    module.start()

    assert module.is_initialized() is True
    assert module.is_running() is True
