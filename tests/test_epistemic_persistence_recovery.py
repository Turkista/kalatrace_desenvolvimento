import unittest

from contracts.iec_contract import IECContract
from contracts.evidence_contract import EvidenceContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import (
    KnowledgeEvolutionEngine,
)


class TestEpistemicPersistenceRecovery(unittest.TestCase):
    def _build_engine(self):
        store = EvidenceStore()
        engine = KnowledgeEvolutionEngine(store)

        iec = IECContract(
            iec_id="IEC-RECOVERY-001",
            title="Teste de recuperação",
            statement="Uma IEC deve sobreviver à reinicialização.",
            knowledge_type="hypothesis",
        )
        engine.register_iec(iec)

        evidence = EvidenceContract(
            id="EV-RECOVERY-001",
            title="Evidência de teste",
            description="Evidência usada para testar persistência.",
            evidence_type="test",
            source="unit-test",
            confidence=0.80,
            quality_score=0.90,
        )
        store.add_evidence(evidence)
        store.link_to_iec(evidence.evidence_id, iec.iec_id, relation="CONTRADICTS", weight=0.75, reason="Teste de reconstrução epistemológica.", metadata={"source": "unit-test"})

        engine.update_state(
            iec.iec_id,
            "SUPPORTED",
            "Teste de persistência",
        )

        engine.register_conflict(
            iec.iec_id,
            iec.iec_id,
            "Conflito sintético de recuperação",
        )

        return store, engine

    def test_evidence_store_round_trip(self):
        store, _ = self._build_engine()
        snapshot = store.to_dict()

        restored = EvidenceStore.from_dict(snapshot)

        self.assertIn("EV-RECOVERY-001", restored.evidences)
        self.assertEqual(
            restored.get_evidence_for_iec("IEC-RECOVERY-001")[0].confidence,
            0.80,
        )
        synthesis = restored.compute_epistemic_synthesis("IEC-RECOVERY-001")
        self.assertEqual(synthesis["support_score"], 0.0)
        self.assertEqual(synthesis["contradiction_score"], 0.80)
        self.assertEqual(synthesis["contradicting_count"], 1)
        relation = restored.get_relations_for_iec("IEC-RECOVERY-001")[0]
        self.assertEqual(relation.relation, "CONTRADICTS")
        self.assertEqual(relation.weight, 0.75)
        self.assertEqual(relation.reason, "Teste de reconstrução epistemológica.")
        self.assertEqual(relation.metadata["source"], "unit-test")

    def test_knowledge_evolution_round_trip(self):
        store, engine = self._build_engine()
        snapshot = engine.to_dict()

        restored = KnowledgeEvolutionEngine.from_dict(snapshot, store)

        state = restored.get_state("IEC-RECOVERY-001")
        self.assertEqual(state["current_state"], "SUPPORTED")
        self.assertEqual(len(state["previous_states"]), 1)
        self.assertEqual(len(restored.list_active_conflicts()), 1)

        conflict = restored.list_active_conflicts()[0]
        self.assertEqual(conflict["conflict_id"], "CONFLICT-1")

        restored.register_conflict(
            "IEC-RECOVERY-001",
            "IEC-RECOVERY-001",
            "Segundo conflito",
        )
        self.assertEqual(
            restored.list_conflicts_for_iec("IEC-RECOVERY-001")[-1]["conflict_id"],
            "CONFLICT-2",
        )


if __name__ == "__main__":
    unittest.main()
