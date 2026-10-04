from typing import Dict, Any, List
from datetime import datetime, UTC

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.state_transition import StateTransitionManager
from engines.knowledge_evolution.evolution_analyzer import EvolutionAnalyzer
from engines.knowledge_evolution.conflict_solver import ConflictSolver
from engines.knowledge_evolution.evidence_merger import EvidenceMerger


class KnowledgeEvolutionEngine:
    """
    Knowledge Evolution Engine (KEE)

    Motor responsável pela evolução
    do conhecimento dentro do KALATRACE.

    Responsabilidades:

    - acompanhar mudanças das IECs;
    - registrar evolução epistemológica;
    - controlar estados do conhecimento;
    - manter histórico evolutivo.

    O KEE não cria conhecimento.
    Ele acompanha sua transformação.

    Migrado de core/knowledge_evolution_engine.py para
    engines/knowledge_evolution/ (T1.3a, sessão de 03/08/2026).

    Split em dois módulos internos (roadmap de estabilização,
    ENGINE-006, sessão de 07/08/2026): StateTransitionManager
    (state_transition.py, estado/transições de cada IEC) e
    EvolutionAnalyzer (evolution_analyzer.py, avaliação de
    evolução via evidências + relatórios/diagnóstico). Esta
    classe passa a ser uma fachada fina que compõe os dois --
    a API pública e o comportamento de eventos são idênticos
    aos de antes do split; nenhum consumidor externo precisa
    mudar (e, checado por busca exaustiva, não havia nenhum
    consumidor de produção usando esta classe antes desta
    sessão).

    evidence_merger.py e conflict_solver.py, os outros dois
    arquivos do pacote, foram implementados em sessão
    posterior (07/08/2026) com base em regra formal real
    (DOCUMENTO 3 — Manual Operacional do Sistema MEDIKALAT +
    KALATRACE, Art. 29º-36º e 73º-78º), trazida pelo usuário.
    Ver o docstring de cada classe (ConflictSolver,
    EvidenceMerger) para o que é regra oficial do documento e
    o que é interpretação desta implementação (principalmente
    os limiares numéricos de severidade/força combinada, que o
    documento não especifica).
    """

    def __init__(self, evidence_store: EvidenceStore):
        self.evidence_store = evidence_store

        self._state_manager = StateTransitionManager()
        self._analyzer = EvolutionAnalyzer(self._state_manager, evidence_store)
        self._conflict_solver = ConflictSolver(self._state_manager, evidence_store)
        self._evidence_merger = EvidenceMerger(self._state_manager, evidence_store)

        # histórico de evolução (eventos do próprio engine, não
        # confundir com o histórico de transições de cada IEC,
        # que fica dentro de StateTransitionManager.iec_states)
        self.evolution_history: List[Dict[str, Any]] = []

    # aliases mantidos por compatibilidade com qualquer código que
    # já lesse diretamente engine.iec_states (nenhum encontrado em
    # produção, mas manter é custo zero e risco zero)
    @property
    def iec_states(self) -> Dict[str, Dict[str, Any]]:
        return self._state_manager.iec_states

    # ==========================================================
    # REGISTRO INTERNO
    # ==========================================================

    def _register_event(self, event: str, details: Dict[str, Any]):
        self.evolution_history.append({
            "event": event,
            "details": details,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    # ==========================================================
    # 1. REGISTRAR IEC
    # ==========================================================

    def register_iec(self, iec: IECContract) -> Dict[str, Any]:
        """Registra uma IEC no sistema de evolução do conhecimento."""
        state = self._state_manager.register_iec(iec)
        self._register_event("iec_registered", state)
        return state

    # ==========================================================
    # 2. OBTER ESTADO ATUAL
    # ==========================================================

    def get_state(self, iec_id: str) -> Dict[str, Any]:
        """Retorna o estado atual de uma IEC."""
        return self._state_manager.get_state(iec_id)

    # ==========================================================
    # 3. ALTERAR ESTADO DO CONHECIMENTO
    # ==========================================================

    def update_state(self, iec_id: str, new_state: str, reason: str) -> Dict[str, Any]:
        """Atualiza o estado epistemológico de uma IEC."""
        current = self._state_manager.update_state(iec_id, new_state, reason)
        transition = current["previous_states"][-1]
        self._register_event("knowledge_state_changed", {
            "iec_id": iec_id,
            "transition": transition,
        })
        return current

    # ==========================================================
    # 4. AVALIAR EVOLUÇÃO AUTOMÁTICA DA IEC
    # ==========================================================

    def evaluate_evolution(self, iec_id: str) -> Dict[str, Any]:
        """Avalia o possível estado evolutivo de uma IEC baseado nas evidências."""
        result = self._analyzer.evaluate_evolution(iec_id)
        self._register_event("evolution_evaluated", result)
        return result

    # ==========================================================
    # 5. APLICAR EVOLUÇÃO SUGERIDA
    # ==========================================================

    def apply_evolution(self, iec_id: str, reason: str) -> Dict[str, Any]:
        """Aplica a evolução sugerida ao estado da IEC."""
        evaluation = self.evaluate_evolution(iec_id)
        return self.update_state(iec_id, evaluation["suggested_state"], reason)

    # ==========================================================
    # 6. ANALISAR REGRESSÃO EPISTEMOLÓGICA
    # ==========================================================

    def analyze_regression(self, iec_id: str) -> Dict[str, Any]:
        """Analisa se uma IEC perdeu sustentação ao longo do tempo."""
        result = self._analyzer.analyze_regression(iec_id)
        self._register_event("regression_analyzed", result)
        return result

    # ==========================================================
    # 7. COMPARAR ESTADOS HISTÓRICOS
    # ==========================================================

    def compare_history(self, iec_id: str) -> Dict[str, Any]:
        """Compara a trajetória histórica de uma IEC."""
        return self._analyzer.compare_history(iec_id)

    # ==========================================================
    # 8. DETECTAR MUDANÇA DE DIREÇÃO
    # ==========================================================

    def detect_direction_change(self, iec_id: str) -> Dict[str, Any]:
        """Detecta se a evolução está fortalecendo ou enfraquecendo o conhecimento."""
        return self._analyzer.detect_direction_change(iec_id)

    # ==========================================================
    # 9. GERAR LINHA DO TEMPO EPISTEMOLÓGICA
    # ==========================================================

    def get_timeline(self, iec_id: str) -> List[Dict[str, Any]]:
        """Retorna a evolução histórica de uma IEC em ordem temporal."""
        return self._analyzer.get_timeline(iec_id)

    # ==========================================================
    # 10. GERAR RESUMO EVOLUTIVO
    # ==========================================================

    def generate_summary(self, iec_id: str) -> Dict[str, Any]:
        """Gera um resumo completo da evolução de uma IEC."""
        summary = self._analyzer.generate_summary(iec_id)
        self._register_event("evolution_summary_generated", summary)
        return summary

    # ==========================================================
    # 11. LISTAR IECs REGISTRADAS
    # ==========================================================

    def list_registered_iecs(self) -> List[str]:
        """Retorna todas as IECs acompanhadas pelo KEE."""
        return self._state_manager.list_registered_iecs()

    # ==========================================================
    # 12. CONTAGEM POR ESTADO
    # ==========================================================

    def state_distribution(self) -> Dict[str, int]:
        """Mostra quantas IECs existem em cada estado epistemológico."""
        return self._state_manager.state_distribution()

    # ==========================================================
    # 13. CONFLITOS EPISTEMOLÓGICOS (DOCUMENTO 3, Art. 73º-77º)
    # ==========================================================

    def register_conflict(self, iec_a_id: str, iec_b_id: str, description: str) -> Dict[str, Any]:
        """Registra um conflito epistemológico entre duas IECs."""
        record = self._conflict_solver.register_conflict(iec_a_id, iec_b_id, description)
        self._register_event("conflict_registered", record)
        return record

    def resolve_conflict(self, conflict_id: str, mechanism: str, outcome: str, note: str) -> Dict[str, Any]:
        """Resolve um conflito ativo (Art. 76º/77º)."""
        record = self._conflict_solver.resolve_conflict(conflict_id, mechanism, outcome, note)
        self._register_event("conflict_resolved", record)
        return record

    def list_active_conflicts(self) -> List[Dict[str, Any]]:
        """Lista conflitos epistemológicos ainda ativos."""
        return self._conflict_solver.list_active_conflicts()

    def list_conflicts_for_iec(self, iec_id: str) -> List[Dict[str, Any]]:
        """Lista conflitos (ativos ou resolvidos) envolvendo uma IEC."""
        return self._conflict_solver.list_conflicts_for_iec(iec_id)

    # ==========================================================
    # 14. MESCLAGEM DE EVIDÊNCIAS (DOCUMENTO 3, Art. 30º-IV)
    # ==========================================================

    def merge_evidence(self, iec_ids: List[str], synthesis_statement: str) -> Dict[str, Any]:
        """Mescla evidências de múltiplas IECs em uma síntese."""
        record = self._evidence_merger.merge_evidence(iec_ids, synthesis_statement)
        self._register_event("evidence_merged", record)
        return record

    # ==========================================================
    # 15. EXPORTAR ESTADO COMPLETO
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Exporta todo o estado interno do KnowledgeEvolutionEngine."""
        return {
            "iec_states": self._state_manager.iec_states,
            "evolution_history": self.evolution_history,
            "conflicts": self._conflict_solver.conflicts,
            "syntheses": self._evidence_merger.syntheses,
        }

    # ==========================================================
    # 16. ESTATÍSTICAS DO MOTOR
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Retorna métricas do KEE."""
        return {
            "registered_iecs": len(self._state_manager.iec_states),
            "evolution_events": len(self.evolution_history),
            "state_distribution": self.state_distribution(),
            "conflicts": self._conflict_solver.stats(),
            "syntheses": self._evidence_merger.stats(),
            "engine": "KnowledgeEvolutionEngine",
            "status": "active",
        }

    # ==========================================================
    # 17. HEALTH CHECK
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """Verifica integridade do motor evolutivo."""
        return {
            "knowledge_evolution_engine": "OK",
            "evidence_store_connected": self.evidence_store is not None,
            "tracked_iecs": len(self._state_manager.iec_states),
        }

    # ==========================================================
    # 18. LIMPAR ESTADO
    # ==========================================================

    def clear(self):
        """Limpa estados e histórico."""
        self._state_manager.clear()
        self.evolution_history.clear()

    # ==========================================================
    # 19. DEBUG
    # ==========================================================

    def __repr__(self) -> str:
        state = self.stats()
        return (
            f"KnowledgeEvolutionEngine("
            f"iecs={state['registered_iecs']}, "
            f"events={state['evolution_events']}, "
            f"status={state['status']}"
            f")"
        )
