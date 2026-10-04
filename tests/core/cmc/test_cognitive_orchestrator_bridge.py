"""
KALATRACE CMC <-> Cognitive Orchestrator Bridge Tests

Validates that the CMC can dispatch Commands to the real,
already-implemented Cognitive Orchestrator (DOCUMENTO 26)
through the ordinary CommandExecutor contract -- without the
CMC ever calling engines directly.
"""

import pytest

from core.cmc import CommandMissionCenter, CognitiveOrchestratorExecutor
from core.command import CommandResult


# =====================================================
# Fixtures: a lightweight fake orchestrator, so most tests
# don't need to spin up the full real engine chain.
# =====================================================


class FakeCognitiveOrchestrator:
    """
    Minimal double implementing the same shape returned by
    CognitiveOrchestrator.run_cycle(), used to test the bridge
    contract without depending on the full engine chain.
    """

    def __init__(self, raise_error: bool = False):

        self.raise_error = raise_error

        self.calls = []

    def run_cycle(self, statement, submitted_by, **kwargs):

        self.calls.append(
            {"statement": statement, "submitted_by": submitted_by}
        )

        if self.raise_error:
            raise RuntimeError("cycle failed")

        class _FakeIEC:
            id = "IEC-TEST-1"

        return {
            "iec": _FakeIEC(),
            "cycle": {"state": "EM_INVESTIGACAO_CONTINUA"},
            "priority": {"priority": 1, "curiosity_level": "CRITICAL"},
            "opportunity": {"composite_score": 0.5},
            "research_plan": None,
        }


# =====================================================
# CognitiveOrchestratorExecutor (contract-level)
# =====================================================


def test_executor_requires_run_cycle_method():

    with pytest.raises(TypeError):
        CognitiveOrchestratorExecutor(object())


def test_executor_rejects_none_orchestrator():

    with pytest.raises(ValueError):
        CognitiveOrchestratorExecutor(None)


def test_executor_name():

    executor = CognitiveOrchestratorExecutor(FakeCognitiveOrchestrator())

    assert executor.name == "cognitive_orchestrator"


def test_executor_execute_success():

    from core.command import Command

    fake = FakeCognitiveOrchestrator()
    executor = CognitiveOrchestratorExecutor(fake, submitted_by="tester")

    command = Command(
        name="Investigate",
        objective="Bakuchiol modula regeneracao cutanea via AMPK",
    )

    result = executor.execute(command)

    assert isinstance(result, CommandResult)
    assert result.success is True
    assert result.data["iec_id"] == "IEC-TEST-1"
    assert result.data["cycle_state"] == "EM_INVESTIGACAO_CONTINUA"

    assert fake.calls[0]["statement"] == command.objective
    assert fake.calls[0]["submitted_by"] == "tester"


def test_executor_execute_failure_is_wrapped_not_raised():

    from core.command import Command

    fake = FakeCognitiveOrchestrator(raise_error=True)
    executor = CognitiveOrchestratorExecutor(fake)

    command = Command(name="Investigate", objective="Something")

    result = executor.execute(command)

    assert result.success is False
    assert "cycle failed" in result.message


# =====================================================
# CommandMissionCenter integration
# =====================================================


def test_cmc_connect_and_execute_with_fake_orchestrator():

    cmc = CommandMissionCenter()

    fake = FakeCognitiveOrchestrator()
    cmc.connect_cognitive_orchestrator(fake)

    mission = cmc.create_mission(
        name="MEDIKALAT Research Mission",
        objective="Evaluate regenerative hypothesis",
    )

    command = cmc.issue_command(
        mission_id=mission.mission_id,
        name="Investigate Bakuchiol AMPK pathway",
        objective="Bakuchiol modula regeneracao cutanea via AMPK",
    )

    result = cmc.execute_command(
        command.command_id,
        executor="cognitive_orchestrator",
    )

    assert result.success is True
    assert command in mission.commands
    assert len(fake.calls) == 1


def test_cmc_connect_cognitive_orchestrator_lazy_default():
    """
    Calling connect_cognitive_orchestrator() with no argument
    should lazily build a real CognitiveOrchestrator and run a
    full cycle against the real engine chain end-to-end.
    """

    cmc = CommandMissionCenter()
    cmc.connect_cognitive_orchestrator()

    mission = cmc.create_mission(
        name="MEDIKALAT Research Mission",
        objective="Evaluate regenerative hypothesis",
    )

    command = cmc.issue_command(
        mission_id=mission.mission_id,
        name="Investigate Resveratrol SIRT1 pathway",
        objective="Resveratrol atua via SIRT1/AMPK na regeneracao muscular",
    )

    result = cmc.execute_command(
        command.command_id,
        executor="cognitive_orchestrator",
    )

    assert result.success is True
    assert result.data["cycle_state"] is not None
    assert result.data["iec_id"] is not None
