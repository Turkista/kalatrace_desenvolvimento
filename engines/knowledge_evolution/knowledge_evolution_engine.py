from typing import Callable, Dict, Any, List, Optional
from datetime import datetime, UTC

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.state_transition import StateTransitionManager
from engines.knowledge_evolution.evolution_analyzer import EvolutionAnalyzer
from engines.knowledge_evolution.conflict_solver import ConflictSolver
from epistemic.conflict_solver import ConflictSolver as WeightedConflictSolver
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

    def __init__(
        self,
        evidence_store: EvidenceStore,
        *,
        event_sink: Optional[Callable[[Optional[str], str, Dict[str, Any]], Any]] = None,
        state_transition_sink: Optional[
            Callable[[str, Optional[str], str, str], Any]
        ] = None,
    ):
        self.evidence_store = evidence_store
        # Optional persistence boundary. The engine remains usable without
        # infrastructure, while repository-backed callers can make events
        # durable without coupling the engine to Supabase.
        self._event_sink = event_sink
        self._state_transition_sink = state_transition_sink

        self._state_manager = StateTransitionManager()
        self._analyzer = EvolutionAnalyzer(self._state_manager, evidence_store)
        self._conflict_solver = ConflictSolver(self._state_manager, evidence_store)
        self._weighted_conflict_solver = WeightedConflictSolver()
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

    @property
    def state_manager(self) -> StateTransitionManager:
        """Expose the state manager used by the evolution engine."""
        return self._state_manager

    # ==========================================================
    # REGISTRO INTERNO
    # ==========================================================

    def _register_event(self, event: str, details: Dict[str, Any]):
        timestamp = datetime.now(UTC).isoformat()
        record = {
            "event": event,
            "details": details,
            "timestamp": timestamp,
        }
        self.evolution_history.append(record)
        if self._event_sink is not None:
            iec_id = details.get("iec_id") if isinstance(details, dict) else None
            self._event_sink(iec_id, event, dict(details))

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
        if self._state_transition_sink is not None:
            self._state_transition_sink(
                iec_id,
                transition.get("from"),
                transition["to"],
                transition.get("reason") or reason,
            )
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

    # ==========================================================\n    # 5. RESOLVER CONFLITO DE EVIDÊNCIAS\n    # ==========================================================\n\n    def resolve_evidence_conflict(self, iec_id: str) -> Dict[str, Any]:\n        \"\"\"Resolve deterministicamente o balanço das evidências de uma IEC.\"\"\"\n        relations = self.evidence_store.get_relations_for_iec(iec_id)\n        links = []\n        for relation in relations:\n            evidence = self.evidence_store.get_evidence(relation.evidence_id)\n            links.append({\n                \"relation\": relation.relation,\n                \"weight\": relation.weight,\n                \"reliability\": evidence.confidence if evidence is not None else 0.0,\n                \"evidence_id\": relation.evidence_id,\n            })\n        decision = self._weighted_conflict_solver.resolve(links)\n        result = {\"iec_id\": iec_id, **decision.to_dict()}\n        self._register_event(\"evidence_conflict_resolved\", result)\n        return result\n\n    # ==========================================================
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
    # 16. RESTAURAR / EXPORTAR ESTADO COMPLETO
    # ==========================================================

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """
        Reconstrói o estado operacional do KEE a partir de um snapshot.

        A restauração recompõe os componentes internos na mesma ordem
        usada na operação normal e não gera novos eventos.
        """
        if not isinstance(snapshot, dict):
            raise TypeError("O snapshot precisa ser um dicionário")

        self._state_manager.restore({
            "iec_states": snapshot.get("iec_states", {})
        })

        self.evolution_history = list(
            snapshot.get("evolution_history", [])
        )

        conflicts = snapshot.get("conflicts", {})
        if not isinstance(conflicts, dict):
            raise ValueError("Snapshot de conflitos inválido")
        self._conflict_solver.conflicts = dict(conflicts)

        syntheses = snapshot.get("syntheses", {})
        if not isinstance(syntheses, dict):
            raise ValueError("Snapshot de sínteses inválido")
        self._evidence_merger.syntheses = dict(syntheses)

        self._conflict_solver._next_id = self._next_numeric_id(
            self._conflict_solver.conflicts,
            "CONFLICT-",
        )
        self._evidence_merger._next_id = self._next_numeric_id(
            self._evidence_merger.syntheses,
            "SYNTHESIS-",
        )

    @staticmethod
    def _next_numeric_id(records: Dict[str, Any], prefix: str) -> int:
        highest = 0
        for record_id in records:
            if not isinstance(record_id, str) or not record_id.startswith(prefix):
                continue
            try:
                highest = max(highest, int(record_id[len(prefix):]))
            except ValueError:
                continue
        return highest + 1

    @classmethod
    def from_dict(
        cls,
        snapshot: Dict[str, Any],
        evidence_store: EvidenceStore,
    ) -> "KnowledgeEvolutionEngine":
        engine = cls(evidence_store)
        engine.restore(snapshot)
        return engine

    # ==========================================================
    # 17. ESTATÍSTICAS DO MOTOR
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
    # 18. HEALTH CHECK
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """Verifica integridade do motor evolutivo."""
        return {
            "knowledge_evolution_engine": "OK",
            "evidence_store_connected": self.evidence_store is not None,
            "tracked_iecs": len(self._state_manager.iec_states),
        }

    # ==========================================================
    # 19. LIMPAR ESTADO
    # ==========================================================

    def clear(self):
        """Limpa estados e histórico."""
        self._state_manager.clear()
        self.evolution_history.clear()

    # ==========================================================
    # 20. DEBUG
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
