from typing import Dict, Any, List

from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_context.scientific_context_engine import ScientificContextEngine
from engines.research_strategy.prioritizer import Prioritizer
from engines.research_strategy.strategy_generator import StrategyGenerator
from engines.research_strategy.planner import ResearchPlanner


class ResearchStrategyEngine:
    """
    Research Strategy Engine (RSE)

    "O RSE é o componente responsável por transformar
    oportunidades científicas identificadas pelo KALATRACE em
    uma estratégia organizada de evolução da pesquisa... Sua
    responsabilidade consiste em auxiliar o pesquisador na
    tomada de decisões estratégicas." (DOCUMENTO 25)

    Terceiro e último módulo novo construído sobre o Cognitive
    Orchestrator (roadmap de estabilização, sessão de
    08/08/2026) -- completa os 3 passos do ciclo oficial
    (DOCUMENTO 26, Art. 5º) que não tinham módulo real
    (Scientific Context Reconstruction e este).

    Fachada que compõe:
    - prioritizer.py (Prioritizer): pontua oportunidades nos
      critérios computáveis do Art. 5º;
    - strategy_generator.py (StrategyGenerator): gera
      recomendação de próximo passo (Art. 7º), sempre
      consultiva (Art. 9º);
    - planner.py (ResearchPlanner): organiza oportunidades
      avaliadas em um plano ranqueado (Art. 6º).

    Ver o docstring de Prioritizer para os 4 critérios
    computáveis vs. os 4 explicitamente não determináveis com
    os dados do projeto hoje.
    """

    def __init__(
        self,
        graph,
        evidence_store: EvidenceStore,
        evolution_engine: KnowledgeEvolutionEngine,
        curiosity_engine: CuriosityEngine,
        context_engine: ScientificContextEngine,
    ):
        self.evidence_store = evidence_store
        self.evolution_engine = evolution_engine
        self.curiosity_engine = curiosity_engine
        self.context_engine = context_engine

        self.prioritizer = Prioritizer(graph, evidence_store, evolution_engine, curiosity_engine)
        self.strategy_generator = StrategyGenerator(evidence_store)
        self.planner = ResearchPlanner()

        # última avaliação de cada oportunidade, por iec_id -- permite
        # montar o plano estratégico (Art. 6º) sobre tudo que já foi
        # avaliado até agora, sem o chamador precisar reunir a lista.
        self.opportunity_history: Dict[str, Dict[str, Any]] = {}

    # ==========================================================
    # AVALIAR UMA OPORTUNIDADE
    # ==========================================================

    def evaluate_opportunity(self, iec_id: str, scr_panorama: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia uma oportunidade científica: pontuação (Art. 5º)
        + recomendação consultiva (Art. 7º).
        """
        priority = self.prioritizer.score(iec_id)
        strategy = self.strategy_generator.generate(iec_id, priority["epistemic_state"], scr_panorama)

        opportunity = {
            "iec_id": iec_id,
            "priority": priority,
            "strategy": strategy,
        }
        self.opportunity_history[iec_id] = opportunity

        return opportunity

    # ==========================================================
    # PLANO ESTRATÉGICO (múltiplas oportunidades, Art. 6º)
    # ==========================================================

    def build_strategic_plan(self, opportunities: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Constrói um plano ranqueado. Sem argumento, usa a última
        avaliação de cada oportunidade já vista (opportunity_history).
        """
        if opportunities is None:
            opportunities = list(self.opportunity_history.values())
        return self.planner.build_plan(opportunities)

    def get_current_plan(self) -> Dict[str, Any]:
        """Retorna o plano estratégico mais recente."""
        return self.planner.get_current_plan()

    # ==========================================================
    # ESTATÍSTICAS
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Estatísticas do RSE."""
        return {
            "plans_generated": len(self.planner.plans),
        }

    def __repr__(self) -> str:
        return f"ResearchStrategyEngine(plans={len(self.planner.plans)})"
