from typing import Dict, Any, List

from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.state_transition import StateTransitionManager


class EvolutionAnalyzer:
    """
    Evolution Analyzer

    Responsável por avaliar, sugerir e analisar a evolução
    epistemológica de IECs a partir das evidências disponíveis
    em um EvidenceStore -- e por gerar diagnóstico/relatório
    sobre a trajetória registrada em um StateTransitionManager.

    Não guarda estado próprio de IEC: lê e escreve através do
    StateTransitionManager que recebe no construtor. Não
    resolve conflito entre IECs concorrentes nem mescla
    evidências de múltiplas fontes -- ver conflict_solver.py e
    evidence_merger.py (ambos ainda não implementados; ver nota
    em engines/knowledge_evolution/__init__.py).

    Extraído de KnowledgeEvolutionEngine (roadmap de
    estabilização, ENGINE-006, sessão de 07/08/2026). Métodos
    movidos aqui sem alteração de comportamento: evaluate_evolution,
    _suggest_state, apply_evolution, analyze_regression,
    compare_history, detect_direction_change, get_timeline,
    generate_summary. KnowledgeEvolutionEngine continua sendo o
    ponto de entrada público -- ele compõe este módulo
    internamente e mantém exatamente a mesma API externa de
    antes do split.
    """

    def __init__(
        self,
        state_manager: StateTransitionManager,
        evidence_store: EvidenceStore,
    ):
        self.state_manager = state_manager
        self.evidence_store = evidence_store

    # ==========================================================
    # 1. AVALIAR EVOLUÇÃO AUTOMÁTICA DA IEC
    # ==========================================================

    def evaluate_evolution(self, iec_id: str) -> Dict[str, Any]:
        """
        Avalia o possível estado evolutivo de uma IEC baseado
        nas evidências.

        Não altera automaticamente. Apenas sugere uma evolução.
        """
        if iec_id not in self.state_manager.iec_states:
            raise ValueError(f"IEC {iec_id} não registrada")

        evidences = self.evidence_store.get_evidence_for_iec(iec_id)
        evidence_count = len(evidences)
        strength = self.evidence_store.compute_evidence_strength(iec_id)
        suggested_state = self._suggest_state(evidence_count, strength)

        return {
            "iec_id": iec_id,
            "evidence_count": evidence_count,
            "evidence_strength": strength,
            "suggested_state": suggested_state,
        }

    # ==========================================================
    # 2. SUGERIR NOVO ESTADO
    # ==========================================================

    def _suggest_state(self, evidence_count: int, strength: float) -> str:
        """Sugere estado epistemológico baseado no suporte atual."""
        if evidence_count == 0:
            return "UNKNOWN"

        if evidence_count >= 5 and strength >= 0.85:
            return "ESTABLISHED"

        if evidence_count >= 3 and strength >= 0.70:
            return "EXPANDING"

        if strength >= 0.50:
            return "SUPPORTED"

        if strength >= 0.25:
            return "QUESTIONED"

        return "NEEDS_REVIEW"

    # ==========================================================
    # 3. APLICAR EVOLUÇÃO SUGERIDA
    # ==========================================================

    def apply_evolution(self, iec_id: str, reason: str) -> Dict[str, Any]:
        """Aplica a evolução sugerida ao estado da IEC."""
        evaluation = self.evaluate_evolution(iec_id)
        new_state = evaluation["suggested_state"]

        return self.state_manager.update_state(iec_id, new_state, reason)

    # ==========================================================
    # 4. ANALISAR REGRESSÃO EPISTEMOLÓGICA
    # ==========================================================

    def analyze_regression(self, iec_id: str) -> Dict[str, Any]:
        """
        Analisa se uma IEC perdeu sustentação ao longo do tempo.

        Procura: queda de força, aumento de incerteza,
        necessidade de revisão.
        """
        state = self.state_manager.get_state(iec_id)
        evidences = self.evidence_store.get_evidence_for_iec(iec_id)

        if not evidences:
            return {
                "iec_id": iec_id,
                "regression": True,
                "reason": "NO_EVIDENCE",
            }

        strength = self.evidence_store.compute_evidence_strength(iec_id)
        current_state = state["current_state"]

        regression = False
        reason = "NO_REGRESSION"

        if current_state in ["ESTABLISHED", "EXPANDING", "SUPPORTED"] and strength < 0.50:
            regression = True
            reason = "REDUCED_EVIDENCE_SUPPORT"

        return {
            "iec_id": iec_id,
            "current_state": current_state,
            "current_strength": strength,
            "regression": regression,
            "reason": reason,
        }

    # ==========================================================
    # 5. COMPARAR ESTADOS HISTÓRICOS
    # ==========================================================

    def compare_history(self, iec_id: str) -> Dict[str, Any]:
        """Compara a trajetória histórica de uma IEC."""
        state = self.state_manager.get_state(iec_id)
        history = state["previous_states"]

        return {
            "iec_id": iec_id,
            "total_transitions": len(history),
            "history": history,
        }

    # ==========================================================
    # 6. DETECTAR MUDANÇA DE DIREÇÃO
    # ==========================================================

    def detect_direction_change(self, iec_id: str) -> Dict[str, Any]:
        """Detecta se a evolução está fortalecendo ou enfraquecendo o conhecimento."""
        state = self.state_manager.get_state(iec_id)
        transitions = state["previous_states"]

        strengthening = 0
        weakening = 0

        positive = [
            ("UNKNOWN", "SUPPORTED"),
            ("SUPPORTED", "EXPANDING"),
            ("EXPANDING", "ESTABLISHED"),
        ]

        negative = [
            ("SUPPORTED", "QUESTIONED"),
            ("EXPANDING", "QUESTIONED"),
            ("QUESTIONED", "NEEDS_REVIEW"),
        ]

        for transition in transitions:
            old = transition["from"]
            new = transition["to"]

            if (old, new) in positive:
                strengthening += 1

            if (old, new) in negative:
                weakening += 1

        if strengthening > weakening:
            direction = "STRENGTHENING"
        elif weakening > strengthening:
            direction = "WEAKENING"
        else:
            direction = "STABLE"

        return {
            "iec_id": iec_id,
            "direction": direction,
            "strengthening_events": strengthening,
            "weakening_events": weakening,
        }

    # ==========================================================
    # 7. GERAR LINHA DO TEMPO EPISTEMOLÓGICA
    # ==========================================================

    def get_timeline(self, iec_id: str) -> List[Dict[str, Any]]:
        """Retorna a evolução histórica de uma IEC em ordem temporal."""
        state = self.state_manager.get_state(iec_id)

        timeline = []
        for transition in state["previous_states"]:
            timeline.append({
                "from": transition["from"],
                "to": transition["to"],
                "reason": transition["reason"],
                "timestamp": transition["timestamp"],
            })

        return timeline

    # ==========================================================
    # 8. GERAR RESUMO EVOLUTIVO
    # ==========================================================

    def generate_summary(self, iec_id: str) -> Dict[str, Any]:
        """Gera um resumo completo da evolução de uma IEC."""
        state = self.state_manager.get_state(iec_id)
        direction = self.detect_direction_change(iec_id)
        regression = self.analyze_regression(iec_id)

        return {
            "iec_id": iec_id,
            "current_state": state["current_state"],
            "total_changes": len(state["previous_states"]),
            "direction": direction["direction"],
            "regression_detected": regression["regression"],
            "timeline": self.get_timeline(iec_id),
        }

    # ==========================================================
    # 9. DEBUG
    # ==========================================================

    def __repr__(self) -> str:
        return f"EvolutionAnalyzer(evidence_store={self.evidence_store!r})"
