from typing import Dict, Any, List

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_context.citation_network import CitationNetwork
from engines.scientific_context.context_builder import ContextBuilder
from engines.scientific_context.timeline import ContextTimeline


class ScientificContextEngine:
    """
    Scientific Context Reconstruction (SCR)

    "Após a aquisição de um novo conhecimento experimental, o
    KALATRACE iniciará automaticamente um processo denominado
    Scientific Context Reconstruction (SCR). O objetivo desse
    processo não consiste em verificar se um resultado está
    correto ou incorreto. Seu propósito é reconstruir o
    contexto científico no qual aquela nova evidência passa a
    existir." (DOCUMENTO 23, Seção 13)

    Implementado (roadmap de estabilização, sessão de
    08/08/2026) como o segundo módulo novo construído sobre o
    Cognitive Orchestrator (o primeiro foi o próprio
    Orchestrator, sessão anterior) -- passo do ciclo oficial
    (DOCUMENTO 26, Art. 5º) que antes era registrado como
    SKIPPED em engines/cognitive_orchestrator/pipeline.py.

    Fachada que compõe:
    - citation_network.py (CitationNetwork): classifica
      relações convergentes/divergentes (Art. 15.1/15.2);
    - context_builder.py (ContextBuilder): monta o Panorama
      Científico completo (Art. 15º/25);
    - timeline.py (ContextTimeline): histórico de
      reconstruções por IEC (Art. 16º).

    Ver o docstring de ContextBuilder para o que é resposta
    real (dados do projeto) e o que é explicitamente marcado
    como não determinável ainda (mecanismos biológicos, novas
    hipóteses) -- nenhuma das duas é fabricada.

    ontology_mapper.py, o quinto arquivo do pacote, segue
    placeholder: mapear IECs para a Ontologia Científica
    (DOCUMENTO 29/30) é um projeto grande por si só, fora do
    escopo desta sessão.
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

        self.citation_network = CitationNetwork(evidence_store, evolution_engine)
        self.context_builder = ContextBuilder(evidence_store, evolution_engine, curiosity_engine, self.citation_network)
        self.timeline = ContextTimeline()

    # ==========================================================
    # RECONSTRUIR CONTEXTO (Art. 13º-19º)
    # ==========================================================

    def reconstruct_context(
        self,
        iec: IECContract,
        connected_iec_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Executa a Scientific Context Reconstruction completa
        para uma IEC -- o Panorama Científico (Art. 25º).
        """
        panorama = self.context_builder.build(iec, connected_iec_ids)

        self.timeline.record_reconstruction(iec.iec_id, {
            "epistemic_state": panorama["current_evidence_state"]["epistemic_state"],
            "consensus": panorama["scientific_consensus"],
            "divergent_count": len(panorama["divergent_evidence"]),
            "convergent_count": len(panorama["convergent_evidence"]),
        })

        return panorama

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_reconstruction_history(self, iec_id: str) -> List[Dict[str, Any]]:
        """Histórico de reconstruções de uma IEC (Art. 16º)."""
        return self.timeline.get_history(iec_id)

    def stats(self) -> Dict[str, Any]:
        """Estatísticas do SCR."""
        return {
            "iecs_with_context": len(self.timeline.history),
            "total_reconstructions": sum(len(h) for h in self.timeline.history.values()),
        }

    def __repr__(self) -> str:
        return f"ScientificContextEngine(iecs={len(self.timeline.history)})"
