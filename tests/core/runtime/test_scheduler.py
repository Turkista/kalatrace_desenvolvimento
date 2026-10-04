"""
KALATRACE Core Runtime - Scheduler Smoke Tests

T1.1b - rede de seguranca minima para core/runtime/scheduler.py,
migrado de kernel/runtime/scheduler.py (achado da T1.1a: capacidade
orfa, sem equivalente previo em core/ e sem nenhum outro ponto do
projeto que a referenciasse antes desta migracao).

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest
from datetime import datetime

from core.runtime import Scheduler, ScheduledTask


class TestScheduledTask:
    def test_creates_with_disabled_last_execution(self):
        task = ScheduledTask(name="t1", function=lambda: 42, interval=10)
        assert task.name == "t1"
        assert task.interval == 10
        assert task.enabled is True
        assert task.last_execution is None

    def test_execute_runs_function_and_stamps_last_execution(self):
        calls = []
        task = ScheduledTask(name="t1", function=lambda: calls.append(1), interval=1)
        result = task.execute()
        assert calls == [1]
        assert isinstance(task.last_execution, datetime)
        assert result is None  # append() returns None

    def test_execute_returns_function_result(self):
        task = ScheduledTask(name="t1", function=lambda: "done", interval=1)
        assert task.execute() == "done"

    def test_disabled_task_does_not_execute(self):
        calls = []
        task = ScheduledTask(name="t1", function=lambda: calls.append(1), interval=1)
        task.enabled = False
        result = task.execute()
        assert calls == []
        assert result is None
        assert task.last_execution is None


class TestScheduler:
    def test_starts_empty_and_not_running(self):
        scheduler = Scheduler()
        assert scheduler.tasks == {}
        assert scheduler.running is False

    def test_register_task_adds_to_tasks(self):
        scheduler = Scheduler()
        scheduler.register_task("t1", lambda: 1, interval=5)
        assert "t1" in scheduler.tasks
        assert scheduler.tasks["t1"].interval == 5

    def test_run_task_executes_registered_task(self):
        scheduler = Scheduler()
        calls = []
        scheduler.register_task("t1", lambda: calls.append(1), interval=5)
        scheduler.run_task("t1")
        assert calls == [1]

    def test_run_task_raises_keyerror_for_unknown_task(self):
        scheduler = Scheduler()
        with pytest.raises(KeyError):
            scheduler.run_task("nao-existe")

    def test_remove_task(self):
        scheduler = Scheduler()
        scheduler.register_task("t1", lambda: 1, interval=5)
        scheduler.remove_task("t1")
        assert "t1" not in scheduler.tasks

    def test_remove_unknown_task_is_noop(self):
        scheduler = Scheduler()
        scheduler.remove_task("nao-existe")  # nao deve levantar excecao

    def test_start_and_stop_toggle_running(self):
        scheduler = Scheduler()
        scheduler.start()
        assert scheduler.running is True
        scheduler.stop()
        assert scheduler.running is False


class TestSchedulerExportedFromCoreRuntime:
    def test_importable_from_core_runtime_package(self):
        from core.runtime import Scheduler as PublicScheduler
        from core.runtime import ScheduledTask as PublicScheduledTask

        assert PublicScheduler is Scheduler
        assert PublicScheduledTask is ScheduledTask
