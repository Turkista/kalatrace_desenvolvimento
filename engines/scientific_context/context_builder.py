from typing import Dict, Any, List
from datetime import datetime, UTC

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_context.citation_network import CitationNetwork


class ContextBuilder:
    """
    Context Builder

    Constrói o Panorama Científico de uma IEC (DOCUMENTO 23,
    Seção 25: "o Panorama Científico não representa uma
    conclusão definitiva. Ele representa o estado atual do
    conhecimento relacionado àquela IEC"), respondendo as 8
    Perguntas Fundamentais da SCR (Seção 15).

    Escopo honesto desta implementação -- nem toda pergunta do
    Art. 15º é respondível com os dados e módulos que existem
    hoje no projeto:

    - 15.1 (convergentes) e 15.2 (divergentes): respondidas via
      CitationNetwork -- ver o docstring de lá sobre o que é
      confirmado e o que é aproximação.
    - 15.3 (similaridade científica): respondida diretamente
      pelas conexões semânticas já inferidas (mesmo dado usado
      para 15.1/15.2).
    - 15.4 (mecanismos biológicos): NÃO respondida
      automaticamente -- exigiria uma ontologia de mecanismos
      biológicos ligada às IECs, que não existe no projeto (ver
      engines/scientific_context/ontology_mapper.py, ainda
      placeholder). Retorna null com o motivo explícito, nunca
      um valor inventado.
    - 15.5 (estado atual da evidência): respondida via
      KnowledgeEvolutionEngine (estado + força de evidência).
    - 15.6 (consenso científico): respondida por uma heurística
      declarada como tal (ver _assess_consensus) a partir da
      distribuição de estados das IECs relacionadas -- não é o
      julgamento de um comitê científico, é um indicador
      derivado dos dados internos do grafo.
    - 15.7 (lacunas científicas): respondida reaproveitando
      CuriosityEngine.analyze_gap (já existente, não duplicado
      aqui).
    - 15.8 (novas hipóteses): NÃO gerada automaticamente --
      exigiria raciocínio combinatório sobre evidências (uma
      capacidade de IA generativa/simbólica que não existe no
      projeto). Retorna lista vazia com o motivo explícito.
    """

    def __init__(
        self,
        evidence_store: EvidenceStore,
        evolution_engine: KnowledgeEvolutionEngine,
        curiosity_engine: CuriosityEngine,
        citation_network: CitationNetwork,
    ):
        self.evidence_store = evidence_store
        self.evolution_engine = evolution_engine
        self.curiosity_engine = curiosity_engine
        self.citation_network = citation_network

    # ==========================================================
    # CONSTRUIR PANORAMA CIENTÍFICO (Art. 15º / Seção 25)
    # ==========================================================

    def build(
        self,
        iec: IECContract,
        connected_iec_ids: List[str],
    ) -> Dict[str, Any]:
        """Constrói o Panorama Científico completo de uma IEC."""

        relations = self.citation_network.classify_relations(iec.iec_id, connected_iec_ids)

        evidence_state = self.evolution_engine.get_state(iec.iec_id)
        evidence_count = len(self.evidence_store.get_evidence_for_iec(iec.iec_id))
        evidence_strength = self.evidence_store.compute_evidence_strength(iec.iec_id)

        gap_analysis = self.curiosity_engine.analyze_gap(iec)

        consensus = self._assess_consensus(relations, evidence_state["current_state"])

        panorama = {
            "iec_id": iec.iec_id,
            "statement": iec.statement,

            # 15.1 / 15.2
            "convergent_evidence": relations["possible_convergent_evidence"],
            "divergent_evidence": relations["divergent_evidence"],

            # 15.3
            "scientific_similarity": connected_iec_ids,

            # 15.4
            "biological_mechanisms": None,

            # 15.5
            "current_evidence_state": {
                "epistemic_state": evidence_state["current_state"],
                "evidence_count": evidence_count,
                "evidence_strength": evidence_strength,
            },

            # 15.6
            "scientific_consensus": consensus,

            # 15.7
            "scientific_gaps": gap_analysis,

            # 15.8
            "new_hypotheses": [],

            # rastreabilidade (Art. 18º)
            "reconstructed_at": datetime.now(UTC).isoformat(),
            "not_determinable": {
                "biological_mechanisms": (
                    "Exigiria ontologia de mecanismos biológicos ligada às IECs "
                    "(DOCUMENTO 29/30) -- não implementada ainda."
                ),
                "new_hypotheses": (
                    "Exigiria raciocínio combinatório sobre evidências -- não "
                    "implementado ainda (DOCUMENTO 23, Seção 15.8)."
                ),
            },
        }

        return panorama

    # ==========================================================
    # HEURÍSTICA DE CONSENSO (15.6) -- ver nota de escopo acima
    # ==========================================================

    def _assess_consensus(self, relations: Dict[str, Any], current_state: str) -> str:
        if relations["divergent_evidence"]:
            return "CONTROVERSIA"

        if current_state in ("UNKNOWN",):
            return "INSUFICIENCIA_DE_EVIDENCIAS"

        if current_state in ("ESTABLISHED", "EXPANDING") and not relations["divergent_evidence"]:
            return "APARENTA_CONSENSO"

        return "INDEFINIDO"

    def __repr__(self) -> str:
        return "ContextBuilder()"
