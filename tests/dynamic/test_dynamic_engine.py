"""
KALATRACE Dynamic -- testes

FASE 5 (PROPOSTA), sessao de 09/08/2026: cobertura de
DynamicEngine/StrategyAdapter (adaptacao do plano do Research
Strategy Engine com os sinais de controversia do Consensus).

Nao pretende ser cobertura completa -- objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_context.scientific_context_engine import ScientificContextEngine
from engines.research_strategy.research_strategy_engine import ResearchStrategyEngine
from consensus.consensus_engine import ConsensusEngine
from dynamic.dynamic_engine import DynamicEngine


class FakeGraph:
    """Grafo minimo -- Prioritizer só usa edges_of()."""

    def edges_of(self, node_id):
        return []


def make_engines():
    evidence_store = EvidenceStore()
    evolution_engine = KnowledgeEvolutionEngine(evidence_store)
    curiosity_engine = CuriosityEngine(evidence_store)
    context_engine = ScientificContextEngine(evidence_store, evolution_engine, curiosity_engine)
    graph = FakeGraph()
    strategy_engine = ResearchStrategyEngine(
        graph, evidence_store, evolution_engine, curiosity_engine, context_engine
    )
    consensus_engine = ConsensusEngine()
    dynamic_engine = DynamicEngine(strategy_engine, consensus_engine)
    return evolution_engine, context_engine, strategy_engine, consensus_engine, dynamic_engine


def register_and_evaluate(evolution_engine, context_engine, strategy_engine, iec_id, statement):
    contract = IECContract(iec_id=iec_id, title=statement[:40], statement=statement, knowledge_type="Observação")
    evolution_engine.register_iec(contract)
    panorama = context_engine.reconstruct_context(contract, connected_iec_ids=[])
    strategy_engine.evaluate_opportunity(iec_id, panorama)
    return panorama


def test_adapt_strategy_sem_oportunidades_retorna_plano_vazio():
    _, _, _, _, dynamic_engine = make_engines()
    result = dynamic_engine.adapt_strategy()

    assert result["adapted_plan"]["ranked_opportunities"] == []


def test_adapt_strategy_sem_controversia_mantem_ranking():
    evolution_engine, context_engine, strategy_engine, consensus_engine, dynamic_engine = make_engines()
    register_and_evaluate(evolution_engine, context_engine, strategy_engine, "IEC-1", "bakuchiol reduz inflamação")

    result = dynamic_engine.adapt_strategy()
    opp = result["adapted_plan"]["ranked_opportunities"][0]

    assert opp["strategy_adjustment"] == "MANTIDA"
    assert opp["adjusted_score"] == opp["priority"]["composite_score"]


def test_adapt_strategy_prioriza_controversia():
    evolution_engine, context_engine, strategy_engine, consensus_engine, dynamic_engine = make_engines()
    register_and_evaluate(evolution_engine, context_engine, strategy_engine, "IEC-1", "bakuchiol reduz inflamação")
    panorama2 = register_and_evaluate(
        evolution_engine, context_engine, strategy_engine, "IEC-2", "resveratrol não tem efeito"
    )

    # Marca IEC-2 como controversa via Consensus
    panorama2_controverso = dict(panorama2)
    panorama2_controverso["scientific_consensus"] = "CONTROVERSIA"
    panorama2_controverso["divergent_evidence"] = ["EV-X"]
    consensus_engine.record_panorama("IEC-2", panorama2_controverso)

    result = dynamic_engine.adapt_strategy()
    controversial_item = next(
        o for o in result["adapted_plan"]["ranked_opportunities"] if o["iec_id"] == "IEC-2"
    )

    assert controversial_item["strategy_adjustment"] == "CONTROVERSIA_PRIORIZADA"
    assert controversial_item["adjusted_score"] > controversial_item["priority"]["composite_score"]


def test_adapt_strategy_mantem_historico():
    evolution_engine, context_engine, strategy_engine, consensus_engine, dynamic_engine = make_engines()
    register_and_evaluate(evolution_engine, context_engine, strategy_engine, "IEC-1", "bakuchiol reduz inflamação")

    dynamic_engine.adapt_strategy()
    dynamic_engine.adapt_strategy()

    assert len(dynamic_engine.get_adapted_plan_history()) == 2
    assert dynamic_engine.get_current_adapted_plan() == dynamic_engine.adapted_plans[-1]


def test_get_current_adapted_plan_sem_historico_levanta_erro():
    _, _, _, _, dynamic_engine = make_engines()
    with pytest.raises(ValueError):
        dynamic_engine.get_current_adapted_plan()
