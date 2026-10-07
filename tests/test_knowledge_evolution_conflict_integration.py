from contracts.iec_contract import IECContract
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from storage.evidence_store import EvidenceStore


def _register(engine: KnowledgeEvolutionEngine, iec_id: str) -> None:
    engine.register_iec(
        IECContract(
            iec_id=iec_id,
            title=iec_id,
            statement=f"statement for {iec_id}",
            knowledge_type="Evidência",
        )
    )


def test_kee_uses_weighted_conflict_solver_during_evolution():
    store = EvidenceStore()
    store.create_evidence(
        "ev-support",
        "source-a",
        "study",
        "support",
        "supporting evidence",
        confidence=0.90,
    )
    store.create_evidence(
        "ev-contradict",
        "source-b",
        "study",
        "contradict",
        "contradicting evidence",
        confidence=0.40,
    )
    store.link_to_iec(
        "ev-support",
        "IEC-1",
        relation="SUPPORTS",
        weight=1.0,
    )
    store.link_to_iec(
        "ev-contradict",
        "IEC-1",
        relation="CONTRADICTS",
        weight=1.0,
    )

    engine = KnowledgeEvolutionEngine(store)
    _register(engine, "IEC-1")

    result = engine.apply_evolution("IEC-1", reason="integration test")

    decision = result["conflict_decision"]
    assert decision["decision"] == "SUPPORTS"
    assert decision["support_score"] == 0.9
    assert decision["contradiction_score"] == 0.4
    assert decision["evidence_count"] == 2

    events = [
        event
        for event in engine.evolution_history
        if event["event"] == "evidence_conflict_resolved"
    ]
    assert len(events) == 1
    assert events[0]["details"]["decision"] == "SUPPORTS"


def test_kee_leaves_balanced_conflict_unresolved():
    store = EvidenceStore()
    store.create_evidence(
        "ev-a",
        "source-a",
        "study",
        "a",
        "evidence a",
        confidence=0.80,
    )
    store.create_evidence(
        "ev-b",
        "source-b",
        "study",
        "b",
        "evidence b",
        confidence=0.80,
    )
    store.link_to_iec("ev-a", "IEC-2", relation="SUPPORTS", weight=1.0)
    store.link_to_iec("ev-b", "IEC-2", relation="CONTRADICTS", weight=1.0)

    engine = KnowledgeEvolutionEngine(store)
    _register(engine, "IEC-2")

    result = engine.apply_evolution("IEC-2", reason="balanced conflict")

    assert result["conflict_decision"]["decision"] == "UNRESOLVED"
    assert result["conflict_decision"]["resolved"] is False


def test_kee_conflict_resolution_does_not_mutate_evidence_store():
    store = EvidenceStore()
    store.create_evidence(
        "ev-neutral",
        "source",
        "study",
        "neutral",
        "neutral evidence",
        confidence=0.70,
    )
    store.link_to_iec("ev-neutral", "IEC-3", relation="NEUTRAL", weight=1.0)

    before = store.to_dict()
    engine = KnowledgeEvolutionEngine(store)
    _register(engine, "IEC-3")

    decision = engine.resolve_evidence_conflict("IEC-3")

    assert decision["decision"] == "UNRESOLVED"
    assert store.to_dict() == before
