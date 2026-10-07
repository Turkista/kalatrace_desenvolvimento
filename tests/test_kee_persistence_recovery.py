import unittest

from persistence.epistemic_repository import EpistemicRepository
from storage.evidence_store import EvidenceStore


class FakeSupabaseClient:
    def __init__(self):
        self.state_transitions = []
        self.events = []

    def record_iec_state_transition(self, access_token, user_id, iec_id, from_state, to_state, reason):
        self.state_transitions.append((iec_id, from_state, to_state, reason))
        return {"ok": True}

    def record_knowledge_evolution_event(self, access_token, user_id, iec_id, event_type, details=None):
        self.events.append((iec_id, event_type, details or {}))
        return {"ok": True}

    def list_iecs(self, access_token, limit=500):
        return [{
            "id": "00000000-0000-0000-0000-000000000001",
            "name": "IEC persistida",
            "statement": "Estado recuperável",
            "methodology": {"knowledge_type": "hypothesis"},
            "result": {"confidence": 0.8, "status": "active", "evidence_ids": []},
            "created_at": "2026-10-07T10:00:00+00:00",
            "updated_at": "2026-10-07T10:00:00+00:00",
        }]

    def list_all_iec_state_history(self, access_token, limit=500):
        return [{
            "iec_id": "00000000-0000-0000-0000-000000000001",
            "from_state": "UNKNOWN",
            "to_state": "SUPPORTED",
            "reason": "Persistência",
            "created_at": "2026-10-07T10:01:00+00:00",
        }]

    def list_knowledge_evolution_events(self, access_token, limit=500):
        return [
            {
                "iec_id": "00000000-0000-0000-0000-000000000001",
                "event_type": "conflict_registered",
                "details": {
                    "conflict_id": "CONFLICT-7",
                    "iec_a_id": "00000000-0000-0000-0000-000000000001",
                    "iec_b_id": "00000000-0000-0000-0000-000000000001",
                    "description": "Conflito persistido",
                    "level": "LEVE",
                    "status": "ATIVO",
                    "resolution": None,
                    "created_at": "2026-10-07T10:02:00+00:00",
                    "resolved_at": None,
                },
                "created_at": "2026-10-07T10:02:00+00:00",
            },
            {
                "iec_id": "00000000-0000-0000-0000-000000000001",
                "event_type": "conflict_resolved",
                "details": {
                    "conflict_id": "CONFLICT-7",
                    "iec_a_id": "00000000-0000-0000-0000-000000000001",
                    "iec_b_id": "00000000-0000-0000-0000-000000000001",
                    "description": "Conflito persistido",
                    "level": "LEVE",
                    "status": "RESOLVIDO",
                    "resolution": {
                        "mechanism": "REVISAO_METODOLOGICA",
                        "outcome": "RESOLVIDO_POR_INTEGRACAO",
                        "note": "Revisão persistida",
                    },
                    "created_at": "2026-10-07T10:02:00+00:00",
                    "resolved_at": "2026-10-07T10:03:00+00:00",
                },
                "created_at": "2026-10-07T10:03:00+00:00",
            },
            {
                "iec_id": "00000000-0000-0000-0000-000000000001",
                "event_type": "evidence_merged",
                "details": {
                    "synthesis_id": "SYNTHESIS-4",
                    "source_iec_ids": ["00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000001"],
                    "statement": "Síntese persistida",
                    "evidence_ids": [],
                    "evidence_count": 0,
                    "combined_strength": 0.0,
                    "created_at": "2026-10-07T10:04:00+00:00",
                },
                "created_at": "2026-10-07T10:04:00+00:00",
            },
        ]

    def list_evidence(self, access_token, limit=500):
        return []

    def list_evidence_iec_links(self, access_token, limit=500):
        return []


class TestKEEPersistenceRecovery(unittest.TestCase):
    def test_reconstructs_state_history_events_conflicts_and_syntheses(self):
        client = FakeSupabaseClient()
        repository = EpistemicRepository(
            client,
            access_token="token",
            user_id="00000000-0000-0000-0000-000000000099",
        )

        store, engine = repository.load_cycle()

        iec_id = "00000000-0000-0000-0000-000000000001"
        self.assertEqual(engine.get_state(iec_id)["current_state"], "SUPPORTED")
        self.assertEqual(len(engine.get_state(iec_id)["previous_states"]), 1)

        self.assertEqual(len(engine.evolution_history), 3)
        self.assertEqual(engine.evolution_history[0]["event"], "conflict_registered")
        self.assertEqual(engine.evolution_history[-1]["event"], "evidence_merged")

        conflicts = engine.list_conflicts_for_iec(iec_id)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["status"], "RESOLVIDO")
        self.assertEqual(
            conflicts[0]["resolution"]["mechanism"],
            "REVISAO_METODOLOGICA",
        )

        self.assertEqual(len(engine._evidence_merger.list_syntheses()), 1)
        self.assertEqual(
            engine._evidence_merger.list_syntheses()[0]["synthesis_id"],
            "SYNTHESIS-4",
        )

        # Recovery must continue numeric identifiers instead of colliding.
        engine.register_conflict(iec_id, iec_id, "Novo conflito")
        self.assertEqual(
            engine.list_conflicts_for_iec(iec_id)[-1]["conflict_id"],
            "CONFLICT-8",
        )

        self.assertIsInstance(store, EvidenceStore)

        engine.update_state(iec_id, "PROVISORIAMENTE_SUPORTADO", "Nova evidência")
        engine.register_conflict(iec_id, iec_id, "Novo conflito persistível")
        engine.merge_evidence([iec_id, iec_id], "Síntese persistível")

        self.assertEqual(len(client.state_transitions), 1)
        self.assertEqual(client.state_transitions[0][0], iec_id)
        self.assertEqual(client.state_transitions[0][2], "PROVISORIAMENTE_SUPORTADO")
        self.assertEqual(
            [event[1] for event in client.events],
            ["knowledge_state_changed", "conflict_registered", "evidence_merged"],
        )

        self.assertIsInstance(store, EvidenceStore)


if __name__ == "__main__":
    unittest.main()
