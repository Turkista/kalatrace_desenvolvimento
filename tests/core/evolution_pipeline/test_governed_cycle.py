from core.evolution_pipeline.governed_cycle import GovernedEvolutionCycle


def test_governed_cycle_proposes_without_execution():
    result = GovernedEvolutionCycle().propose({"id": "m1", "objective": "Improve tests"})
    assert result["next_state"] == "planning"
    assert result["approval_required"] is True
    assert result["plan"]["execution_spec"]["operation"] == "plan_only"
