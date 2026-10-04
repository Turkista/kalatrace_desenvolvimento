from typing import Dict, Any, List

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from discovery_lab.hypothesis_builder import HypothesisBuilder


class DiscoveryLabEngine:
    """
    Discovery Lab

    "Discovery Lab representa o laboratório de descoberta e
    formulação de novas hipóteses do KALATRACE... transformar
    conexões, padrões e observações em hipóteses estruturadas que
    possam ser posteriormente analisadas, simuladas e validadas."
    (discovery_lab/README.md)

    Segundo módulo novo da FASE 5 (PROPOSTA -- roadmap de
    estabilização, sessão de 09/08/2026). README lista "Horse,
    StarHouse, Knowledge, Graph, PARSI" como fontes de entrada --
    Horse, StarHouse e PARSI não existem no projeto hoje (ver
    investigação da FASE 5, sessão de 08/08/2026). Esta
    implementação usa apenas o que é real: Knowledge (via
    EvidenceStore/KnowledgeEvolutionEngine) e Graph (via as
    conexões já inferidas, recebidas de quem chama -- mesmo padrão
    de ScientificContextEngine.reconstruct_context, que também
    recebe connected_iec_ids em vez de consultar o grafo
    diretamente).

    Fachada que compõe:
    - hypothesis_builder.py (HypothesisBuilder): classifica e
      estrutura os candidatos a hipótese.

    Reaproveita CuriosityEngine.analyze_gap e .generate_questions
    (já existentes, não duplicados aqui) -- mesma lacuna que a SCR
    já consulta para a Seção 15.7.
    """

    def __init__(
        self,
        evidence_store: EvidenceStore,
        evolution_engine: KnowledgeEvolutionEngine,
        curiosity_engine: CuriosityEngine,
    ):
        self.evidence_store = evidence_store
        self.evolution_engine = evolution_engine
        self.curiosity_engine = curiosity_engine
        self.builder = HypothesisBuilder()

        # candidatos já gerados, por iec_id -- nunca sobrescritos,
        # mesmo princípio geral do DOCUMENTO 30 já usado nos outros
        # módulos novos (ConsensusTracker, ContextTimeline, etc.).
        self.candidates: Dict[str, List[Dict[str, Any]]] = {}

    # ==========================================================
    # GERAR CANDIDATO A HIPÓTESE PARA UMA IEC
    # ==========================================================

    def generate_hypothesis_candidate(self, iec_id: str, connected_iec_ids: List[str]) -> Dict[str, Any]:
        """
        Gera um candidato a hipótese estruturado para uma IEC, a
        partir da lacuna de conhecimento (CuriosityEngine) e das
        conexões já inferidas no grafo para ela.
        """
        state = self.evolution_engine.get_state(iec_id)
        contract = IECContract(
            iec_id=iec_id,
            title=state["statement"][:40],
            statement=state["statement"],
            knowledge_type="Conhecimento",
        )

        gap = self.curiosity_engine.analyze_gap(contract)
        questions = self.curiosity_engine.generate_questions(contract)

        candidate = self.builder.build_candidate(
            iec_id=iec_id,
            statement=state["statement"],
            gap=gap,
            questions=questions,
            connected_iec_ids=connected_iec_ids,
        )
        self.candidates.setdefault(iec_id, []).append(candidate)

        return candidate

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_candidates(self, iec_id: str) -> List[Dict[str, Any]]:
        return self.candidates.get(iec_id, [])

    def qualifying_candidates(self) -> List[Dict[str, Any]]:
        """Todos os candidatos já gerados que qualificam (curiosity_level CRITICAL/HIGH/MEDIUM)."""
        return [
            candidate
            for candidates in self.candidates.values()
            for candidate in candidates
            if candidate["qualifies_as_candidate"]
        ]

    def stats(self) -> Dict[str, Any]:
        all_candidates = [c for cs in self.candidates.values() for c in cs]
        return {
            "iecs_with_candidates": len(self.candidates),
            "total_candidates": len(all_candidates),
            "qualifying_candidates": len(self.qualifying_candidates()),
            "gap_conectado": len([c for c in all_candidates if c["exploration_type"] == "GAP_CONECTADO"]),
            "gap_isolado": len([c for c in all_candidates if c["exploration_type"] == "GAP_ISOLADO"]),
        }

    def __repr__(self) -> str:
        return f"DiscoveryLabEngine(iecs={len(self.candidates)})"
