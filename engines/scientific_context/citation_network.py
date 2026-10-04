from typing import Dict, Any, List

from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine


class CitationNetwork:
    """
    Citation Network

    Responsável pela parte do Scientific Context Reconstruction
    (DOCUMENTO 23, Seção 15.1 "Evidências Convergentes" e 15.2
    "Evidências Divergentes") que classifica IECs relacionadas a
    uma IEC nova.

    Escopo honesto desta implementação: uma conexão inferida por
    similaridade semântica (engines/cognitive_orchestrator/pipeline.py,
    via inference.infer) indica que duas IECs falam do mesmo
    assunto -- não indica se elas concordam ou discordam. Não há,
    em nenhum documento oficial consultado até agora, um algoritmo
    para determinar concordância/discordância automaticamente a
    partir do texto (o mesmo limite já registrado em
    conflict_solver.py). Por isso:

    - "divergente" aqui usa uma fonte real e verificável: conflitos
      já registrados no ConflictSolver (via
      KnowledgeEvolutionEngine.list_conflicts_for_iec) envolvendo a
      IEC -- alguém (humano ou Engine de raciocínio) já identificou
      a divergência explicitamente;
    - "convergente" é uma aproximação declarada como tal: IECs
      conectadas por similaridade semântica que NÃO estão em
      conflito registrado. Não é confirmação de concordância
      científica -- é ausência de divergência conhecida sobre um
      tópico relacionado. O campo is_confirmed_convergence deixa
      isso explícito no retorno.
    """

    def __init__(
        self,
        evidence_store: EvidenceStore,
        evolution_engine: KnowledgeEvolutionEngine,
    ):
        self.evidence_store = evidence_store
        self.evolution_engine = evolution_engine

    # ==========================================================
    # 1. CLASSIFICAR RELAÇÕES DE UMA IEC
    # ==========================================================

    def classify_relations(
        self,
        iec_id: str,
        connected_iec_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Classifica as IECs conectadas a iec_id em divergentes
        (conflito já registrado) e possíveis convergentes
        (conectadas, sem conflito registrado).
        """
        conflicts = self.evolution_engine.list_conflicts_for_iec(iec_id)
        conflicting_ids = set()
        for conflict in conflicts:
            other = conflict["iec_b_id"] if conflict["iec_a_id"] == iec_id else conflict["iec_a_id"]
            conflicting_ids.add(other)

        divergent = [
            {
                "iec_id": cid,
                "conflicts": [c for c in conflicts if cid in (c["iec_a_id"], c["iec_b_id"])],
            }
            for cid in connected_iec_ids
            if cid in conflicting_ids
        ]

        possible_convergent = [
            {"iec_id": cid, "is_confirmed_convergence": False}
            for cid in connected_iec_ids
            if cid not in conflicting_ids
        ]

        return {
            "iec_id": iec_id,
            "divergent_evidence": divergent,
            "possible_convergent_evidence": possible_convergent,
        }

    def __repr__(self) -> str:
        return "CitationNetwork()"
