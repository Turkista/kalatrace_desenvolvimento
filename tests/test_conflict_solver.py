from epistemic.conflict_solver import (
    CONTRADICTS,
    DECISION_CONTRADICTS,
    DECISION_SUPPORTS,
    DECISION_UNRESOLVED,
    SUPPORTS,
    ConflictSolver,
)


def test_supporting_evidence_wins_by_weighted_strength():
    result = ConflictSolver().resolve(
        [
            {"evidence_id": "e1", "relation": SUPPORTS, "weight": 0.9, "reliability": 1.0},
            {"evidence_id": "e2", "relation": CONTRADICTS, "weight": 0.4, "reliability": 1.0},
        ]
    )

    assert result.decision == DECISION_SUPPORTS
    assert result.support_score == 0.9
    assert result.contradiction_score == 0.4
    assert result.margin == 0.5


def test_reliability_modulates_evidence_strength():
    result = ConflictSolver().resolve(
        [
            {"evidence_id": "e1", "relation": SUPPORTS, "weight": 1.0, "reliability": 0.4},
            {"evidence_id": "e2", "relation": CONTRADICTS, "weight": 0.7, "reliability": 1.0},
        ]
    )

    assert result.decision == DECISION_CONTRADICTS
    assert result.support_score == 0.4
    assert result.contradiction_score == 0.7


def test_balanced_conflict_remains_unresolved():
    result = ConflictSolver(minimum_margin=0.05).resolve(
        [
            {"evidence_id": "e1", "relation": SUPPORTS, "weight": 0.5},
            {"evidence_id": "e2", "relation": CONTRADICTS, "weight": 0.48},
        ]
    )

    assert result.decision == DECISION_UNRESOLVED
    assert result.resolved is False


def test_neutral_evidence_does_not_choose_a_side():
    result = ConflictSolver().resolve(
        [{"evidence_id": "e1", "relation": "NEUTRAL", "weight": 1.0}]
    )

    assert result.decision == DECISION_UNRESOLVED
    assert result.support_score == 0.0
    assert result.contradiction_score == 0.0


def test_invalid_relation_is_rejected():
    try:
        ConflictSolver().resolve(
            [{"evidence_id": "e1", "relation": "UNKNOWN", "weight": 1.0}]
        )
    except ValueError as exc:
        assert "Unsupported evidence relation" in str(exc)
    else:
        raise AssertionError("Expected invalid relation to raise ValueError")


def test_result_is_serializable_for_evolution_event():
    result = ConflictSolver().resolve(
        [{"evidence_id": "e1", "relation": SUPPORTS, "weight": 0.8}]
    )

    payload = result.to_dict()

    assert payload["decision"] == DECISION_SUPPORTS
    assert payload["evidence_ids"] == ["e1"]
    assert payload["resolved"] is True
