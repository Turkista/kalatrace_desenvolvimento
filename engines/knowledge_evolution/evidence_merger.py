from typing import Dict, Any, List
from datetime import datetime, UTC

from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.state_transition import StateTransitionManager


class EvidenceMerger:
    """
    Evidence Merger

    Responsável por mesclar evidências de múltiplas IECs em
    uma síntese, seguindo o vocabulário formal do DOCUMENTO 3
    (Manual Operacional do Sistema MEDIKALAT + KALATRACE):

    - Art. 30º, IV: "Conexão de integração: síntese de
      múltiplos nós" -- um dos 5 tipos oficiais de conexão
      entre nós no KALATRACE;
    - Art. 76º, III: "integração de múltiplas fontes" -- um
      dos 5 mecanismos oficiais de resolução de conflito
      (ver conflict_solver.py).

    Escopo desta implementação (roadmap de estabilização,
    sessão de 07/08/2026): o DOCUMENTO 3 nomeia a "síntese de
    múltiplos nós" como um tipo de conexão válido, mas não
    especifica a fórmula de agregação -- como combinar a força
    de evidências de proveniências e confiabilidades
    diferentes em um único número. A fórmula usada aqui (média
    ponderada pela confiança de cada evidência individual, via
    EvidenceStore.compute_evidence_strength sobre o conjunto
    unificado) é a interpretação desta implementação, no mesmo
    espírito das faixas já assumidas em
    evolution_analyzer.py/conflict_solver.py -- sujeita a
    calibração futura caso o time científico traga uma fórmula
    diferente.

    Este módulo NÃO decide se duas IECs devem ser mescladas --
    essa decisão pertence a quem chama (um humano, o
    ConflictSolver como mecanismo de resolução, ou um Engine de
    raciocínio). Ele só executa a mesclagem depois de decidida.
    """

    def __init__(
        self,
        state_manager: StateTransitionManager,
        evidence_store: EvidenceStore,
    ):
        self.state_manager = state_manager
        self.evidence_store = evidence_store

        # sínteses já produzidas, por id
        self.syntheses: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1

    # ==========================================================
    # 1. MESCLAR EVIDÊNCIAS (Art. 30º, IV / Art. 76º, III)
    # ==========================================================

    def merge_evidence(
        self,
        iec_ids: List[str],
        synthesis_statement: str,
    ) -> Dict[str, Any]:
        """
        Mescla as evidências de múltiplas IECs em uma síntese.

        Não cria uma nova IEC nem altera o grafo -- retorna o
        registro da síntese (evidências unificadas + força
        combinada), para que quem chamou decida o que fazer com
        ela (criar uma nova IEC via CoreEngine, aplicar
        apply_evolution, resolver um conflito via
        ConflictSolver.resolve_conflict com mechanism=
        "INTEGRACAO_MULTIPLAS_FONTES", etc.).
        """
        if len(iec_ids) < 2:
            raise ValueError(
                "merge_evidence precisa de pelo menos 2 IECs (Art. 30º, IV: "
                "\"síntese de múltiplos nós\")"
            )

        for iec_id in iec_ids:
            if iec_id not in self.state_manager.iec_states:
                raise ValueError(f"IEC {iec_id} não registrada")

        all_evidence_ids: List[str] = []
        for iec_id in iec_ids:
            for evidence in self.evidence_store.get_evidence_for_iec(iec_id):
                if evidence.evidence_id not in all_evidence_ids:
                    all_evidence_ids.append(evidence.evidence_id)

        combined_strength = self._compute_combined_strength(all_evidence_ids)

        synthesis_id = f"SYNTHESIS-{self._next_id}"
        self._next_id += 1

        record = {
            "synthesis_id": synthesis_id,
            "source_iec_ids": list(iec_ids),
            "statement": synthesis_statement,
            "evidence_ids": all_evidence_ids,
            "evidence_count": len(all_evidence_ids),
            "combined_strength": combined_strength,
            "created_at": datetime.now(UTC).isoformat(),
        }

        self.syntheses[synthesis_id] = record

        return record

    # ==========================================================
    # 2. FORÇA COMBINADA
    # ==========================================================

    def _compute_combined_strength(self, evidence_ids: List[str]) -> float:
        """Ver nota de escopo no docstring da classe sobre esta fórmula."""
        if not evidence_ids:
            return 0.0

        confidences = [
            self.evidence_store.evidences[eid].confidence
            for eid in evidence_ids
            if eid in self.evidence_store.evidences
        ]

        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)

    # ==========================================================
    # 3. CONSULTAS
    # ==========================================================

    def get_synthesis(self, synthesis_id: str) -> Dict[str, Any]:
        """Retorna uma síntese pelo id."""
        if synthesis_id not in self.syntheses:
            raise ValueError(f"Síntese {synthesis_id} não registrada")
        return self.syntheses[synthesis_id]

    def list_syntheses(self) -> List[Dict[str, Any]]:
        """Lista todas as sínteses já produzidas."""
        return list(self.syntheses.values())

    def stats(self) -> Dict[str, Any]:
        """Estatísticas das sínteses produzidas."""
        return {
            "total_syntheses": len(self.syntheses),
        }

    def __repr__(self) -> str:
        return f"EvidenceMerger(syntheses={len(self.syntheses)})"
