from core.agent_planning.coding_planner import CodingPlanner


def test_planner_never_auto_approves():
    plan = CodingPlanner().plan("m1", "Refactor the API")
    assert plan.requires_approval is True
    assert plan.execution_spec["operation"] == "plan_only"
    assert plan.risk == "low"


def test_planner_flags_high_risk_objectives():
    plan = CodingPlanner().plan("m1", "Delete production migration")
    assert plan.risk == "high"


def test_execution_spec_requires_explicit_code_operations():
    try:
        CodingPlanner.validate_execution_spec({"operation": "code_apply"})
    except ValueError:
        pass
    else:
        raise AssertionError("code_apply without explicit operations must be rejected")
