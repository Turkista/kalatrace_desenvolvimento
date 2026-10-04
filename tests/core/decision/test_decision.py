"""
KALATRACE Decision Controller Tests

Validates decision creation, oversight fields, lifecycle
transitions, and confidence estimation.
"""

import pytest

from core.decision import (
    Decision,
    DecisionStatus,
    DecisionStateMachine,
    DecisionRegistry,
    DecisionController,
)


# =====================================================
# Decision entity
# =====================================================


def test_create_decision():

    decision = Decision(
        action="Prioritize IEC-045",
        reason="3 independent studies + mechanistic compatibility + low contradiction level",
        confidence=0.82,
        evidence=["Liu et al. 2020", "Lim et al. 2019", "Zhu 2021"],
        alternatives=["Deprioritize pending replication"],
    )

    assert decision.action == "Prioritize IEC-045"
    assert decision.confidence == 0.82
    assert decision.status == DecisionStatus.PROPOSED
    assert len(decision.evidence) == 3
    assert len(decision.alternatives) == 1


def test_decision_requires_action_and_reason():

    with pytest.raises(ValueError):
        Decision(action="", reason="some reason")

    with pytest.raises(ValueError):
        Decision(action="Do something", reason="")


def test_decision_confidence_bounds():

    with pytest.raises(ValueError):
        Decision(action="A", reason="B", confidence=1.5)

    with pytest.raises(ValueError):
        Decision(action="A", reason="B", confidence=-0.1)


def test_decision_accept_and_reject():

    accepted = Decision(action="A", reason="B")
    accepted.accept()
    assert accepted.status == DecisionStatus.ACCEPTED

    rejected = Decision(action="A", reason="B")
    rejected.reject()
    assert rejected.status == DecisionStatus.REJECTED


def test_decision_supersede():

    decision = Decision(action="A", reason="B")
    decision.accept()

    decision.supersede("other-decision-id")

    assert decision.status == DecisionStatus.SUPERSEDED
    assert decision.superseded_by == "other-decision-id"


# =====================================================
# Decision state machine
# =====================================================


def test_state_machine_valid_transition():

    assert DecisionStateMachine.can_transition(
        DecisionStatus.PROPOSED,
        DecisionStatus.ACCEPTED,
    )


def test_state_machine_invalid_transition():

    assert not DecisionStateMachine.can_transition(
        DecisionStatus.REJECTED,
        DecisionStatus.ACCEPTED,
    )

    with pytest.raises(ValueError):
        DecisionStateMachine.transition(
            DecisionStatus.REJECTED,
            DecisionStatus.ACCEPTED,
        )


# =====================================================
# Decision registry
# =====================================================


def test_decision_registry():

    registry = DecisionRegistry()

    decision = Decision(action="A", reason="B", mission_id="mission-1")

    registry.register(decision)

    assert registry.count() == 1
    assert registry.get(decision.decision_id) == decision
    assert registry.list_by_mission("mission-1") == [decision]


def test_decision_registry_rejects_duplicates():

    registry = DecisionRegistry()

    decision = Decision(action="A", reason="B")

    registry.register(decision)

    with pytest.raises(ValueError):
        registry.register(decision)


# =====================================================
# Decision controller
# =====================================================


def test_controller_record_and_accept():

    controller = DecisionController()

    decision = controller.record_decision(
        action="Prioritize IEC-045",
        reason="Strong mechanistic evidence",
        confidence=0.75,
        mission_id="mission-1",
    )

    assert decision.status == DecisionStatus.PROPOSED

    accepted = controller.accept_decision(decision.decision_id)

    assert accepted.status == DecisionStatus.ACCEPTED
    assert controller.list_by_mission("mission-1") == [decision]


def test_controller_supersede_requires_existing_target():

    controller = DecisionController()

    decision = controller.record_decision(action="A", reason="B")
    controller.accept_decision(decision.decision_id)

    with pytest.raises(ValueError):
        controller.supersede_decision(decision.decision_id, "does-not-exist")


def test_controller_estimate_confidence_matches_specification_example():

    controller = DecisionController()

    # Specification example: 3 independent studies + mechanistic
    # compatibility + low contradiction level -> confidence ~0.82
    confidence = controller.estimate_confidence(
        evidence_count=3,
        mechanistic_compatibility=True,
        contradiction_level="LOW",
    )

    assert 0.75 <= confidence <= 0.90


def test_controller_estimate_confidence_bounds():

    controller = DecisionController()

    high_contradiction = controller.estimate_confidence(
        evidence_count=0,
        mechanistic_compatibility=False,
        contradiction_level="HIGH",
    )

    assert high_contradiction == 0.0

    with pytest.raises(ValueError):
        controller.estimate_confidence(evidence_count=-1)

    with pytest.raises(ValueError):
        controller.estimate_confidence(
            evidence_count=1,
            contradiction_level="UNKNOWN_LEVEL",
        )
