from typing import Dict, Any, List, Optional

from consensus.consensus_tracker import ConsensusTracker


class ConsensusEngine:
    """
    Consensus

    "Consensus representa a capacidade de análise de consenso e
    divergência científica do KALATRACE... avaliar o grau de
    concordância, controvérsia e estabilidade de determinado
    conhecimento dentro do universo científico." (consensus/README.md)

    Primeiro módulo novo da FASE 5 (PROPOSTA -- roadmap de
    estabilização, sessão de 09/08/2026), implementado sobre o
    que já existe: consome o histórico de reconstruções de
    contexto científico produzido pela Scientific Context
    Reconstruction (SCR) -- README lista "Knowledge, Graph,
    Evidence Registry, Validation Engine, Research Engine" como
    fontes; nesta implementação o dado real disponível é o
    Panorama Científico da SCR (`scientific_consensus`,
    `divergent_evidence`, `convergent_evidence`), que já agrega
    Graph + Evidence Registry + Knowledge Evolution.

    Escopo honesto -- o que este módulo NÃO faz (README,
    "Limitações": "Consensus não valida uma informação sozinho...
    não substitui evidências científicas"):
    - não julga controvérsia entre grupos de pesquisadores ou
      afiliações reais -- o projeto não modela autoria/afiliação;
    - não recalcula consenso -- usa a heurística já declarada do
      ContextBuilder (SCR), não duplica nem substitui;
    - "estabilidade" aqui é estritamente: a classificação de
      consenso mudou ou não entre reconstruções sucessivas da SCR
      para a mesma IEC -- não uma medida epistemológica nova.

    Fachada que compõe:
    - consensus_tracker.py (ConsensusTracker): histórico e
      detecção de mudança de classificação por IEC.
    """

    NOT_DETERMINABLE = {
        "divergencia_entre_pesquisadores": (
            "Exigiria modelar autores/afiliações e suas posições -- não "
            "implementado no projeto (o grafo relaciona IECs, não pessoas)."
        ),
        "consenso_de_comite_cientifico": (
            "Consensus não substitui um julgamento humano formal (README, "
            "Limitações) -- a classificação vem de uma heurística interna "
            "sobre a distribuição de estados das IECs relacionadas."
        ),
    }

    def __init__(self):
        self.tracker = ConsensusTracker()

    # ==========================================================
    # REGISTRAR UM PANORAMA CIENTÍFICO (SAÍDA DA SCR)
    # ==========================================================

    def record_panorama(self, iec_id: str, scr_panorama: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra a classificação de consenso de um Panorama
        Científico (ScientificContextEngine.reconstruct_context)
        e retorna se essa classificação mudou desde o registro
        anterior desta IEC (mudança de paradigma, se houver).
        """
        entry = self.tracker.record(
            iec_id,
            consensus_state=scr_panorama["scientific_consensus"],
            divergent_count=len(scr_panorama.get("divergent_evidence", [])),
            convergent_count=len(scr_panorama.get("convergent_evidence", [])),
        )
        shift = self.tracker.detect_shift(iec_id)

        return {
            "iec_id": iec_id,
            "recorded": entry,
            "paradigm_shift": shift,
            "not_determinable": dict(self.NOT_DETERMINABLE),
        }

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def assess_stability(self, iec_id: str) -> Dict[str, Any]:
        """
        Estabilidade do conhecimento desta IEC no sentido restrito
        descrito no docstring da classe: quantas reconstruções já
        existem e se a classificação de consenso mudou na última.
        """
        history = self.tracker.get_history(iec_id)
        if not history:
            return {
                "iec_id": iec_id,
                "status": "SEM_HISTORICO",
                "reason": "Nenhum Panorama Científico registrado para esta IEC ainda.",
            }

        shift = self.tracker.detect_shift(iec_id)
        status = "EM_MUDANCA" if shift else "ESTAVEL" if len(history) > 1 else "HISTORICO_INSUFICIENTE"

        return {
            "iec_id": iec_id,
            "status": status,
            "reconstructions": len(history),
            "current_state": history[-1]["consensus_state"],
            "last_shift": shift,
        }

    def controversial_iecs(self) -> List[str]:
        """IECs cuja classificação mais recente é CONTROVERSIA (SCR 15.6)."""
        return [
            iec_id for iec_id in self.tracker.all_tracked_iecs()
            if self.tracker.latest(iec_id) and self.tracker.latest(iec_id)["consensus_state"] == "CONTROVERSIA"
        ]

    def consensus_landscape(self) -> Dict[str, Any]:
        """
        Panorama agregado: distribuição da classificação de
        consenso mais recente entre todas as IECs já observadas
        por este módulo.
        """
        distribution: Dict[str, int] = {}
        for iec_id in self.tracker.all_tracked_iecs():
            latest = self.tracker.latest(iec_id)
            if latest is None:
                continue
            state = latest["consensus_state"]
            distribution[state] = distribution.get(state, 0) + 1

        return {
            "tracked_iecs": len(self.tracker.all_tracked_iecs()),
            "distribution": distribution,
            "controversial_count": len(self.controversial_iecs()),
        }

    def get_history(self, iec_id: str) -> List[Dict[str, Any]]:
        return self.tracker.get_history(iec_id)

    def stats(self) -> Dict[str, Any]:
        return {
            "tracked_iecs": len(self.tracker.all_tracked_iecs()),
            "controversial_iecs": len(self.controversial_iecs()),
        }

    def __repr__(self) -> str:
        return f"ConsensusEngine(iecs={len(self.tracker.all_tracked_iecs())})"
