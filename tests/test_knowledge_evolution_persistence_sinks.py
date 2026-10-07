from contracts.evidence_contract import EvidenceContract
from contracts.iec_contract import IECContract
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from storage.evidence_store import EvidenceStore


def test_kee_emits_persistence_sinks_for_events_and_state_transitions():
    events = []
    transitions = []
    store = EvidenceStore()
    engine = KnowledgeEvolutionEngine(
        store,
        event_sink=lambda iec_id, event, details: events.append(
            (iec_id, event, details)
        ),
        state_transition_sink=lambda iec_id, old, new, reason: transitions.append(
            (iec_id, old, new, reason)
        ),
    )

    iec = IECContract(
        iec_id="IEC-PERSIST-001",
        statement="Estado epistemológico persistível",
        knowledge_type="observacao",
    )
    engine.register_iec(iec)
    engine.apply_evolution(iec.iec_id, reason="teste de persistência")

    assert any(event == "iec_registered" for _, event, _ in events)
    assert any(event == "evolution_evaluated" for _, event, _ in events)
    assert any(event == "evidence_conflict_resolved" for _, event, _ in events)
    assert any(event == "knowledge_state_changed" for _, event, _ in events)
    assert transitions
    assert transitions[-1][0] == iec.iec_id
    assert transitions[-1][2] == engine.get_state(iec.iec_id)["current_state"]
