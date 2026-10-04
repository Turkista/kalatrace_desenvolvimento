"""
KALATRACE CMC <-> Cognitive Orchestrator Bridge

Connects the Command & Mission Center's Command Layer to the
already-implemented Cognitive Orchestrator (DOCUMENTO 26,
engines/cognitive_orchestrator/), using the CommandExecutor
contract that already exists for this exact purpose (see
core.command.command_dispatcher.CommandDispatcher: "Executors
may represent: Agents, Engines, Skills, External workers").

This module deliberately does NOT create a second coordinator
for engine execution. DOCUMENTO 26, Art. 7 states: "Os modulos
do KALATRACE nao deverao depender diretamente uns dos outros.
Toda comunicacao ocorrera por intermedio do Cognitive
Orchestrator." The CognitiveOrchestrator remains the only
component deciding how the scientific cognitive cycle runs;
the CMC only dispatches a Command to it -- exactly as it would
dispatch to any other executor -- and receives the cycle
report back as a CommandResult.

Scope note: DOCUMENTO 26 coordinates a per-IEC (per knowledge
submission) cycle, not a per-mission workflow. A single Mission
in the CMC sense may therefore issue several commands to the
Cognitive Orchestrator over its lifetime (one per piece of
knowledge it wants investigated); the CMC does not assume a
1:1 relationship between Mission and cognitive cycle.
"""

from __future__ import annotations

from typing import Any

from core.command.command import Command
from core.command.command_executor import CommandExecutor
from core.command.command_result import CommandResult


class CognitiveOrchestratorExecutor(CommandExecutor):
    """
    Adapts a CognitiveOrchestrator instance to the
    CommandExecutor contract.

    Command.objective is used as the cycle's submission
    "statement" (DOCUMENTO 26, Art. 5, evento "nova submissao
    manual"). The resulting cycle report is wrapped into a
    CommandResult so the CMC keeps a uniform result shape
    regardless of which executor actually ran the command.
    """

    def __init__(
        self,
        cognitive_orchestrator: Any,
        submitted_by: str = "Command & Mission Center",
    ) -> None:
        """
        Wraps a CognitiveOrchestrator instance.

        The orchestrator is injected rather than constructed
        here, since CognitiveOrchestrator owns real engine
        state (knowledge graph, evidence store, etc.) that
        should typically be created once and shared, not
        re-created per executor.
        """

        if cognitive_orchestrator is None:
            raise ValueError(
                "cognitive_orchestrator cannot be None."
            )

        if not hasattr(cognitive_orchestrator, "run_cycle"):
            raise TypeError(
                "cognitive_orchestrator must implement run_cycle()."
            )

        if not isinstance(submitted_by, str) or not submitted_by.strip():
            raise ValueError(
                "submitted_by cannot be empty."
            )

        self.cognitive_orchestrator = cognitive_orchestrator

        self.submitted_by = submitted_by.strip()

    @property
    def name(self) -> str:
        """
        Executor identifier used for registration and routing.
        """

        return "cognitive_orchestrator"

    def execute(self, command: Command) -> CommandResult:
        """
        Runs one full DOCUMENTO 26 cognitive cycle for the
        command's objective and returns the outcome as a
        CommandResult.
        """

        if not isinstance(command, Command):
            raise TypeError(
                "execute() requires a Command instance."
            )

        try:

            cycle_result = self.cognitive_orchestrator.run_cycle(
                statement=command.objective,
                submitted_by=self.submitted_by,
            )

        except Exception as exc:

            return CommandResult.failure_result(
                command_id=command.command_id,
                message=f"Cognitive cycle failed: {exc}",
                executor=self.name,
            )

        cycle = cycle_result.get("cycle", {})

        cycle_state = cycle.get("state")

        iec = cycle_result.get("iec")

        return CommandResult.success_result(
            command_id=command.command_id,
            message=f"Cognitive cycle completed: {cycle_state}",
            data={

                "iec_id": getattr(iec, "id", None),

                "cycle_state": cycle_state,

                "priority": cycle_result.get("priority"),

                "opportunity": cycle_result.get("opportunity"),

                "research_plan": cycle_result.get("research_plan"),

            },
            executor=self.name,
        )

    def __repr__(self) -> str:

        return (
            f"<CognitiveOrchestratorExecutor "
            f"submitted_by={self.submitted_by!r}>"
        )
