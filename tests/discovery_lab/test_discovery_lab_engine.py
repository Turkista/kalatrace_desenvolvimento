"""
KALATRACE Discovery Lab -- testes

FASE 5 (PROPOSTA), sessao de 09/08/2026: cobertura de
DiscoveryLabEngine/HypothesisBuilder (geracao de candidato a
hipotese a partir da lacuna do CuriosityEngine + conexoes do
grafo).

Nao pretende ser cobertura completa -- objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from discovery_lab.discovery_lab_engine import DiscoveryLabEngine


def make_engine():
    evidence_store = EvidenceStore()
    evolution_engine = KnowledgeEvolutionEngine(evidence_store)
    curiosity_engine = CuriosityEngine(evidence_store)
    discovery_lab = DiscoveryLabEngine(evidence_store, evolution_engine, curiosity_engine)
    return evidence_store, evolution_engine, curiosity_engine, discovery_lab


def register_iec(evolution_engine, iec_id, statement):
    contract = IECContract(iec_id=iec_id, title=statement[:40], statement=statement, knowledge_type="Observação")
    evolution_engine.register_iec(contract)
    return contract


def test_gap_isolado_sem_conexoes():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")

    candidate = discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=[])

    assert candidate["exploration_type"] == "GAP_ISOLADO"
    assert candidate["connected_iec_ids"] == []


def test_gap_conectado_com_conexoes():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")

    candidate = discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=["IEC-2", "IEC-3"])

    assert candidate["exploration_type"] == "GAP_CONECTADO"
    assert candidate["connected_iec_ids"] == ["IEC-2", "IEC-3"]


def test_sem_evidencia_curiosidade_critical_qualifica():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")

    candidate = discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=[])

    assert candidate["curiosity_level"] == "CRITICAL"
    assert candidate["qualifies_as_candidate"] is True


def test_hypothesis_text_nunca_fabricado():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")

    candidate = discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=[])

    assert candidate["hypothesis_text"] is None
    assert "hypothesis_text" in candidate["not_determinable"]


def test_candidatos_acumulam_historico_por_iec():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")

    discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=[])
    discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=["IEC-2"])

    history = discovery_lab.get_candidates("IEC-1")
    assert len(history) == 2
    assert history[0]["exploration_type"] == "GAP_ISOLADO"
    assert history[1]["exploration_type"] == "GAP_CONECTADO"


def test_stats_agrega_corretamente():
    _, evolution_engine, _, discovery_lab = make_engine()
    register_iec(evolution_engine, "IEC-1", "bakuchiol reduz inflamação")
    register_iec(evolution_engine, "IEC-2", "resveratrol ativa SIRT1")

    discovery_lab.generate_hypothesis_candidate("IEC-1", connected_iec_ids=[])
    discovery_lab.generate_hypothesis_candidate("IEC-2", connected_iec_ids=["IEC-1"])

    stats = discovery_lab.stats()
    assert stats["iecs_with_candidates"] == 2
    assert stats["total_candidates"] == 2
    assert stats["gap_isolado"] == 1
    assert stats["gap_conectado"] == 1
