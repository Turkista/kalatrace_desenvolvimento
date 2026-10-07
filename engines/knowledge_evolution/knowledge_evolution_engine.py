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

    O KEE não cria conhecimento.
    Ele acompanha sua transformação.
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
        self._event_sink = event_sink
        self._state_transition_sink = state_transition_sink

        self._state_manager = StateTransitionManager()
        self._analyzer = EvolutionAnalyzer(self._state_manager, evidence_store)
        self._conflict_solver = ConflictSolver(self._state_manager, evidence_store)
        self._weighted_conflict_solver = WeightedConflictSolver()
        self._evidence_merger = EvidenceMerger(self._state_manager, evidence_store)

        self.evolution_history: List[Dict[str, Any]] = []

    @property
    def iec_states(self) -> Dict[str, Dict[str, Any]]:
        return self._state_manager.iec_states

    @property
    def state_manager(self) -> StateTransitionManager:
        return self._state_manager

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

    def register_iec(self, iec: IECContract) -> Dict[str, Any]:
        state = self._state_manager.register_iec(iec)
        self._register_event("iec_registered", state)
        return state

    def get_state(self, iec_id: str) -> Dict[str, Any]:
        return self._state_manager.get_state(iec_id)

    def update_state(self, iec_id: str, new_state: str, reason: str) -> Dict[str, Any]:
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

    def evaluate_evolution(self, iec_id: str) -> Dict[str, Any]:
        result = self._analyzer.evaluate_evolution(iec_id)
        self._register_event("evolution_evaluated", result)
        return result

    def resolve_evidence_conflict(self, iec_id: str) -> Dict[str, Any]:
        relations = self.evidence_store.get_relations_for_iec(iec_id)
        links = []
        for relation in relations:
            evidence = self.evidence_store.get_evidence(relation.evidence_id)
            links.append({
                "relation": relation.relation,
                "weight": relation.weight,
                "reliability": evidence.confidence if evidence is not None else 0.0,
                "evidence_id": relation.evidence_id,
            })
        decision = self._weighted_conflict_solver.resolve(links)
        result = {"iec_id": iec_id, **decision.to_dict()}
        self._register_event("evidence_conflict_resolved", result)
        return result

    def apply_evolution(self, iec_id: str, reason: str) -> Dict[str, Any]:
        """Aplica a evolução sugerida e expõe a decisão de conflito no resultado."""
        evaluation = self.evaluate_evolution(iec_id)
        conflict_decision = self.resolve_evidence_conflict(iec_id)
        updated_state = self.update_state(
            iec_id,
            evaluation["suggested_state"],
            reason,
        )
        return {
            **updated_state,
            "conflict_decision": conflict_decision,
        }

    def analyze_regression(self, iec_id: str) -> Dict[str, Any]:
        result = self._analyzer.analyze_regression(iec_id)
        self._register_event("regression_analyzed", result)
        return result

    def compare_history(self, iec_id: str) -> Dict[str, Any]:
        return self._analyzer.compare_history(iec_id)

    def detect_direction_change(self, iec_id: str) -> Dict[str, Any]:
        return self._analyzer.detect_direction_change(iec_id)

    def get_timeline(self, iec_id: str) -> List[Dict[str, Any]]:
        return self._analyzer.get_timeline(iec_id)

    def generate_summary(self, iec_id: str) -> Dict[str, Any]:
        summary = self._analyzer.generate_summary(iec_id)
        self._register_event("evolution_summary_generated", summary)
        return summary

    def list_registered_iecs(self) -> List[str]:
        return self._state_manager.list_registered_iecs()

    def state_distribution(self) -> Dict[str, int]:
        return self._state_manager.state_distribution()

    def register_conflict(self, iec_a_id: str, iec_b_id: str, description: str) -> Dict[str, Any]:
        record = self._conflict_solver.register_conflict(iec_a_id, iec_b_id, description)
        self._register_event("conflict_registered", record)
        return record

    def resolve_conflict(self, conflict_id: str, mechanism: str, outcome: str, note: str) -> Dict[str, Any]:
        record = self._conflict_solver.resolve_conflict(conflict_id, mechanism, outcome, note)
        self._register_event("conflict_resolved", record)
        return record

    def list_active_conflicts(self) -> List[Dict[str, Any]]:
        return self._conflict_solver.list_active_conflicts()

    def list_conflicts_for_iec(self, iec_id: str) -> List[Dict[str, Any]]:
        return self._conflict_solver.list_conflicts_for_iec(iec_id)

    def merge_evidence(self, iec_ids: List[str], synthesis_statement: str) -> Dict[str, Any]:
        record = self._evidence_merger.merge_evidence(iec_ids, synthesis_statement)
        self._register_event("evidence_merged", record)
        return record

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iec_states": self._state_manager.iec_states,
            "evolution_history": self.evolution_history,
            "conflicts": self._conflict_solver.conflicts,
            "syntheses": self._evidence_merger.syntheses,
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        if not isinstance(snapshot, dict):
            raise TypeError("O snapshot precisa ser um dicionário")

        self._state_manager.restore({
            "iec_states": snapshot.get("iec_states", {})
        })
        self.evolution_history = list(snapshot.get("evolution_history", []))

        conflicts = snapshot.get("conflicts", {})
        if not isinstance(conflicts, dict):
            raise ValueError("Snapshot de conflitos inválido")
        self._conflict_solver.conflicts = dict(conflicts)

        syntheses = snapshot.get("syntheses", {})
        if not isinstance(syntheses, dict):
            raise ValueError("Snapshot de sínteses inválido")
        self._evidence_merger.syntheses = dict(syntheses)

        self._conflict_solver._next_id = self._next_numeric_id(
            self._conflict_solver.conflicts, "CONFLICT-"
        )
        self._evidence_merger._next_id = self._next_numeric_id(
            self._evidence_merger.syntheses, "SYNTHESIS-"
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

    def stats(self) -> Dict[str, Any]:
        return {
            "registered_iecs": len(self._state_manager.iec_states),
            "evolution_events": len(self.evolution_history),
            "state_distribution": self.state_distribution(),
            "conflicts": self._conflict_solver.stats(),
            "syntheses": self._evidence_merger.stats(),
            "engine": "KnowledgeEvolutionEngine",
            "status": "active",
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "knowledge_evolution_engine": "OK",
            "evidence_store_connected": self.evidence_store is not None,
            "tracked_iecs": len(self._state_manager.iec_states),
        }

    def clear(self):
        self._state_manager.clear()
        self.evolution_history.clear()

    def __repr__(self) -> str:
        state = self.stats()
        return (
            f"KnowledgeEvolutionEngine("
            f"iecs={state['registered_iecs']}, "
            f"events={state['evolution_events']}, "
            f"status={state['status']}"
            f")"
        )
