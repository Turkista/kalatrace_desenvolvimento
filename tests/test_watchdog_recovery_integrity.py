from types import SimpleNamespace

import pytest

from persistence.epistemic_repository import EpistemicRepository
from storage.evidence_store import EvidenceStore


def _runtime(store, *, iec_id="IEC-1"):
    return SimpleNamespace(
        state_manager=SimpleNamespace(
            iec_states={
                iec_id: {
                    "iec_id": iec_id,
                    "current_state": "VALIDATED",
                }
            }
        ),
        evolution_history=[{"event": "state_changed"}],
    )


def test_validate_recovery_integrity_accepts_consistent_runtime():
    store = EvidenceStore()
    store.evidences["E-1"] = object()
    store.relations["E-1:IEC-1:epistemic"] = SimpleNamespace(
        evidence_id="E-1",
        iec_id="IEC-1",
    )
    store.iec_index["IEC-1"] = {"E-1"}
    store.iec_relation_index["IEC-1"] = {"E-1:IEC-1:epistemic"}

    result = EpistemicRepository.validate_recovery_integrity(
        store,
        _runtime(store),
    )

    assert result == {
        "evidence_count": 1,
        "relation_count": 1,
        "iec_count": 1,
        "evolution_event_count": 1,
        "integrity_errors": 0,
    }


def test_validate_recovery_integrity_fails_on_orphan_relation():
    store = EvidenceStore()
    store.relations["orphan"] = SimpleNamespace(
        evidence_id="MISSING",
        iec_id="IEC-1",
    )

    with pytest.raises(RuntimeError, match="missing evidence"):
        EpistemicRepository.validate_recovery_integrity(
            store,
            _runtime(store),
        )
