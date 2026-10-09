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
                    "source_iec_ids": [
                        "00000000-0000-0000-0000-000000000001",
                        "00000000-0000-0000-0000-000000000001",
                    ],
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
    def _repository(self, client):
        return EpistemicRepository(
            client,
            access_token="token",
            user_id="00000000-0000-0000-0000-000000000099",
        )

    def test_reconstructs_state_history_events_conflicts_and_syntheses(self):
        client = FakeSupabaseClient()
        repository = self._repository(client)

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
            [event[1] for event in client.events[-3:]],
            ["knowledge_state_changed", "conflict_registered", "evidence_merged"],
        )

    def test_recovery_is_idempotent_and_does_not_emit_persistence_writes(self):
        client = FakeSupabaseClient()
        repository = self._repository(client)

        store_a, engine_a = repository.load_cycle()
        store_b, engine_b = repository.load_cycle()

        # Hydration uses direct reconstruction and must not replay engine
        # mutations through persistence sinks.
        self.assertEqual(client.state_transitions, [])
        self.assertEqual(client.events, [])

        self.assertEqual(store_a.to_dict(), store_b.to_dict())
        self.assertEqual(store_a.history, [])
        self.assertEqual(store_b.history, [])
        self.assertEqual(engine_a.to_dict(), engine_b.to_dict())

        # A second recovery starts from a fresh runtime and therefore must
        # not append duplicate state transitions or evolution events.
        self.assertEqual(len(engine_a.get_state(
            "00000000-0000-0000-0000-000000000001"
        )["previous_states"]), 1)
        self.assertEqual(len(engine_b.get_state(
            "00000000-0000-0000-0000-000000000001"
        )["previous_states"]), 1)
        self.assertEqual(len(engine_a.evolution_history), 3)
        self.assertEqual(len(engine_b.evolution_history), 3)

        # Numeric identifiers are reconstructed deterministically as well.
        engine_a.register_conflict(
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000001",
            "Novo conflito A",
        )
        engine_b.register_conflict(
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000001",
            "Novo conflito B",
        )
        self.assertEqual(
            engine_a.list_conflicts_for_iec(
                "00000000-0000-0000-0000-000000000001"
            )[-1]["conflict_id"],
            "CONFLICT-8",
        )
        self.assertEqual(
            engine_b.list_conflicts_for_iec(
                "00000000-0000-0000-0000-000000000001"
            )[-1]["conflict_id"],
            "CONFLICT-8",
        )


    def test_reconstructs_multiple_iecs_evidence_and_all_epistemic_relations(self):
        client = FakeSupabaseClient()
        client._iecs = [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "IEC A",
                "statement": "Primeira IEC",
                "methodology": {"knowledge_type": "hypothesis"},
                "result": {"confidence": 0.8, "status": "active", "evidence_ids": ["E1", "E2"]},
                "created_at": "2026-10-07T11:00:00+00:00",
                "updated_at": "2026-10-07T11:00:00+00:00",
            },
            {
                "id": "00000000-0000-0000-0000-000000000002",
                "name": "IEC B",
                "statement": "Segunda IEC",
                "methodology": {"knowledge_type": "observation"},
                "result": {"confidence": 0.6, "status": "active", "evidence_ids": ["E2", "E3"]},
                "created_at": "2026-10-07T11:01:00+00:00",
                "updated_at": "2026-10-07T11:01:00+00:00",
            },
        ]
        client._evidence = [
            {
                "id": "E1", "title": "Evidência 1", "description": "Suporte",
                "evidence_type": "paper", "source": "Fonte A", "confidence": 0.9,
                "quality_score": 0.8, "version": 1,
                "created_at": "2026-10-07T11:02:00+00:00",
                "updated_at": "2026-10-07T11:02:00+00:00", "metadata": {},
            },
            {
                "id": "E2", "title": "Evidência 2", "description": "Contradição",
                "evidence_type": "study", "source": "Fonte B", "confidence": 0.7,
                "quality_score": 0.7, "version": 1,
                "created_at": "2026-10-07T11:03:00+00:00",
                "updated_at": "2026-10-07T11:03:00+00:00", "metadata": {},
            },
            {
                "id": "E3", "title": "Evidência 3", "description": "Contexto",
                "evidence_type": "review", "source": "Fonte C", "confidence": 0.5,
                "quality_score": 0.6, "version": 1,
                "created_at": "2026-10-07T11:04:00+00:00",
                "updated_at": "2026-10-07T11:04:00+00:00", "metadata": {},
            },
        ]
        client._links = [
            {"evidence_id": "E1", "iec_id": "00000000-0000-0000-0000-000000000001",
             "relation": "SUPPORTS", "weight": 0.8, "reason": "Suporte direto", "metadata": {"source": "A"}},
            {"evidence_id": "E2", "iec_id": "00000000-0000-0000-0000-000000000001",
             "relation": "CONTRADICTS", "weight": 0.6, "reason": "Resultado contrário", "metadata": {"source": "B"}},
            {"evidence_id": "E2", "iec_id": "00000000-0000-0000-0000-000000000002",
             "relation": "SUPPORTS", "weight": 0.5, "reason": "Suporte parcial", "metadata": {}},
            {"evidence_id": "E3", "iec_id": "00000000-0000-0000-0000-000000000002",
             "relation": "NEUTRAL", "weight": 1.0, "reason": "Contexto", "metadata": {"kind": "context"}},
        ]

        def list_iecs(access_token, limit=500):
            return list(client._iecs)

        def list_evidence(access_token, limit=500):
            return list(client._evidence)

        def list_links(access_token, limit=500):
            return list(client._links)

        client.list_iecs = list_iecs
        client.list_evidence = list_evidence
        client.list_evidence_iec_links = list_links
        client.list_all_iec_state_history = lambda access_token, limit=500: []
        client.list_knowledge_evolution_events = lambda access_token, limit=500: []

        repository = self._repository(client)
        store_a, engine_a = repository.load_cycle()
        store_b, engine_b = repository.load_cycle()

        self.assertEqual(len(store_a.evidences), 3)
        self.assertEqual(len(store_a.relations), 4)
        self.assertEqual(len(store_a.get_relations_for_iec("00000000-0000-0000-0000-000000000001")), 2)
        self.assertEqual(len(store_a.get_relations_for_iec("00000000-0000-0000-0000-000000000002")), 2)

        relation_a = store_a.get_relation("E1", "00000000-0000-0000-0000-000000000001")
        relation_b = store_a.get_relation("E2", "00000000-0000-0000-0000-000000000001")
        relation_c = store_a.get_relation("E2", "00000000-0000-0000-0000-000000000002")
        relation_d = store_a.get_relation("E3", "00000000-0000-0000-0000-000000000002")

        self.assertEqual(relation_a.relation, "SUPPORTS")
        self.assertEqual(relation_b.relation, "CONTRADICTS")
        self.assertEqual(relation_c.relation, "SUPPORTS")
        self.assertEqual(relation_d.relation, "NEUTRAL")
        self.assertEqual(relation_a.weight, 0.8)
        self.assertEqual(relation_b.reason, "Resultado contrário")
        self.assertEqual(relation_d.metadata["kind"], "context")
        # Legacy links without created_at use the stable evidence timestamp.
        self.assertEqual(relation_a.created_at, "2026-10-07T11:02:00+00:00")
        self.assertEqual(
            engine_a.get_state("00000000-0000-0000-0000-000000000001")["created_at"],
            "2026-10-07T11:00:00+00:00",
        )

        synthesis_a = store_a.compute_epistemic_synthesis("00000000-0000-0000-0000-000000000001")
        self.assertEqual(synthesis_a["evidence_count"], 2)
        self.assertEqual(synthesis_a["supporting_count"], 1)
        self.assertEqual(synthesis_a["contradicting_count"], 1)
        self.assertEqual(synthesis_a["neutral_count"], 0)

        synthesis_b = store_a.compute_epistemic_synthesis("00000000-0000-0000-0000-000000000002")
        self.assertEqual(synthesis_b["evidence_count"], 2)
        self.assertEqual(synthesis_b["supporting_count"], 1)
        self.assertEqual(synthesis_b["contradicting_count"], 0)
        self.assertEqual(synthesis_b["neutral_count"], 1)

        self.assertEqual(store_a.to_dict(), store_b.to_dict())
        self.assertEqual(engine_a.to_dict(), engine_b.to_dict())
        self.assertEqual(client.state_transitions, [])
        self.assertEqual(client.events, [])


    def test_pagination_does_not_truncate_at_500(self):
        from integrations.supabase import SupabaseClient, SupabaseSettings

        client = SupabaseClient(
            SupabaseSettings(url="https://example.invalid", publishable_key="test")
        )
        calls = []

        def fake_select(table, access_token, *, select="*", filters=None):
            calls.append(dict(filters or {}))
            offset = int((filters or {}).get("offset", "0"))
            limit = int((filters or {}).get("limit", "500"))
            total = 1001
            remaining = max(total - offset, 0)
            size = min(limit, remaining)
            return [{"id": offset + i} for i in range(size)]

        client.select = fake_select

        rows = client._select_all_pages(
            "knowledge_evolution_events",
            "token",
            filters={"order": "created_at.asc"},
        )

        self.assertEqual(len(rows), 1001)
        self.assertEqual(calls[0]["limit"], "500")
        self.assertEqual(calls[0]["offset"], "0")
        self.assertEqual(calls[1]["offset"], "500")
        self.assertEqual(calls[2]["offset"], "1000")
        self.assertEqual(len(calls), 3)

        limited = client._select_all_pages(
            "knowledge_evolution_events",
            "token",
            filters={"order": "created_at.asc"},
            max_rows=750,
        )
        self.assertEqual(len(limited), 750)


if __name__ == "__main__":
    unittest.main()
