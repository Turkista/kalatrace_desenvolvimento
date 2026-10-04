"""
KALATRACE Core

Runtime Scheduler

Interval-based task scheduling for runtime
components. Migrated from kernel/runtime/scheduler.py
as part of ADR-001 (T1.1b) — orphan capability with
no equivalent in core/runtime prior to this migration.
"""

from typing import Dict, Callable
from datetime import datetime, timezone


class ScheduledTask:
    """
    Representa uma tarefa agendada.
    """

    def __init__(
        self,
        name: str,
        function: Callable,
        interval: int
    ):
        self.name = name
        self.function = function
        self.interval = interval
        self.last_execution = None
        self.enabled = True

    def execute(self):
        """
        Executa a tarefa.
        """

        if not self.enabled:
            return

        result = self.function()

        self.last_execution = datetime.now(
            timezone.utc
        )

        return result


class Scheduler:
    """
    Kernel Scheduler

    Responsável pelo gerenciamento
    de tarefas programadas.
    """

    def __init__(self):
        self.tasks: Dict[
            str,
            ScheduledTask
        ] = {}

        self.running = False

    def register_task(
        self,
        name: str,
        function: Callable,
        interval: int
    ):
        """
        Registra uma tarefa.
        """

        task = ScheduledTask(
            name,
            function,
            interval
        )

        self.tasks[name] = task

        print(
            f"Tarefa registrada: {name}"
        )

    def run_task(
        self,
        name: str
    ):
        """
        Executa uma tarefa específica.
        """

        if name not in self.tasks:
            raise KeyError(
                f"Tarefa inexistente: {name}"
            )

        return self.tasks[name].execute()

    def remove_task(
        self,
        name: str
    ):
        """
        Remove uma tarefa.
        """

        if name in self.tasks:
            del self.tasks[name]

    def start(self):
        """
        Inicia o Scheduler.
        """

        self.running = True

        print(
            "Scheduler iniciado."
        )

    def stop(self):
        """
        Para o Scheduler.
        """

        self.running = False

        print(
            "Scheduler encerrado."
        )