"""Repository for reconstructing the KALATRACE epistemic cycle from Supabase.

Supabase is the durable source for evidence, IEC state transitions and
evolution events. EvidenceStore and KnowledgeEvolutionEngine are rebuilt from
those records after process restart.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional, Tuple

from contracts.evidence_contract import EvidenceContract
from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from integrations.supabase import SupabaseClient


class EpistemicRepository:
    """Persistence boundary for the durable epistemic state."""

    def __init__(self, client: SupabaseClient, *, access_token: str, user_id: str) -> None:
        if not access_token:
            raise ValueError("access_token é obrigatório.")
        if not user_id:
            raise ValueError("user_id é obrigatório.")
        self.client = client
        self.access_token = access_token
        self.user_id = user_id

    def save_evidence(self, evidence: EvidenceContract) -> Any:
        evidence.validate()
        return self.client.persist_evidence(self.access_token, self.user_id, evidence)

    def link_evidence(
        self,
        evidence_id: str,
        iec_id: str,
        *,
        relation: str = "SUPPORTS",
        weight: float = 1.0,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Persist an epistemic Evidence -> IEC relation without losing semantics."""
        relation = str(relation or "SUPPORTS").upper().strip()
        if relation not in {"SUPPORTS", "CONTRADICTS", "NEUTRAL"}:
            raise ValueError("Relação epistemológica inválida.")
        if not 0.0 <= float(weight) <= 1.0:
            raise ValueError("weight deve estar entre 0 e 1.")

        return self.client.link_evidence_to_iec(
            self.access_token,
            self.user_id,
            evidence_id,
            iec_id,
            relation,
            float(weight),
            reason,
            metadata if isinstance(metadata, dict) else {},
        )

    def record_evidence_change(
        self,
        evidence_id: str,
        event_type: str,
        *,
        previous_confidence: Optional[float] = None,
        new_confidence: Optional[float] = None,
        reason: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.client.record_evidence_history(
            self.access_token,
            self.user_id,
            evidence_id,
            event_type,
            previous_confidence=previous_confidence,
            new_confidence=new_confidence,
            reason=reason,
            payload=payload,
        )

    def record_state_transition(
        self, iec_id: str, from_state: Optional[str], to_state: str, reason: str
    ) -> Any:
        return self.client.record_iec_state_transition(
            self.access_token, self.user_id, iec_id, from_state, to_state, reason
        )

    def record_evolution_event(
        self, iec_id: Optional[str], event_type: str, details: Optional[Dict[str, Any]] = None
    ) -> Any:
        return self.client.record_knowledge_evolution_event(
            self.access_token, self.user_id, iec_id, event_type, details
        )

    def load_evidence_store(self, *, limit: Optional[int] = None) -> EvidenceStore:
        """Rebuild EvidenceStore from durable evidence and IEC links."""
        rows = self.client.list_evidence(self.access_token, limit=limit)
        store = EvidenceStore()

        for row in rows or []:
            store.add_evidence(EvidenceContract.from_dict(row))

        links = self.client.list_evidence_iec_links(self.access_token, limit=limit)
        for link in links or []:
            evidence_id = link.get("evidence_id")
            iec_id = link.get("iec_id")
            if evidence_id and iec_id:
                store.link_to_iec(evidence_id, iec_id, relation=str(link.get("relation") or "SUPPORTS").upper().strip(), weight=float(link.get("weight", 1.0) or 0.0), reason=str(link.get("reason") or ""), metadata=link.get("metadata") if isinstance(link.get("metadata"), dict) else {})

        return store

    def load_evolution_engine(
        self,
        evidence_store: EvidenceStore,
        *,
        iec_ids: Optional[list[str]] = None,
        limit: Optional[int] = None,
    ) -> KnowledgeEvolutionEngine:
        """Rebuild current epistemological state and its transition history."""
        engine = KnowledgeEvolutionEngine(
            evidence_store=evidence_store,
            event_sink=self.record_evolution_event,
            state_transition_sink=self.record_state_transition,
        )
        selected = set(iec_ids) if iec_ids is not None else None

        for row in self.client.list_iecs(self.access_token, limit=limit) or []:
            current_id = self._iec_id(row)
            if not current_id or (selected is not None and current_id not in selected):
                continue
            engine.state_manager.register_iec(self._iec_from_row(row))

        for row in self.client.list_all_iec_state_history(
            self.access_token, limit=limit
        ) or []:
            current_id = row.get("iec_id")
            if not current_id or (selected is not None and current_id not in selected):
                continue

            if current_id not in engine.state_manager.iec_states:
                engine.state_manager.iec_states[current_id] = {
                    "iec_id": current_id,
                    "statement": "",
                    "current_state": row.get("to_state") or "UNKNOWN",
                    "previous_states": [],
                    "created_at": row.get("created_at"),
                }

            state = engine.state_manager.iec_states[current_id]
            state["previous_states"].append({
                "from": row.get("from_state"),
                "to": row.get("to_state"),
                "reason": row.get("reason") or "",
                "timestamp": row.get("created_at"),
            })
            if row.get("to_state"):
                state["current_state"] = row["to_state"]

        # The event stream is the durable source for KEE-level history.
        # It also contains full conflict/synthesis records emitted by the
        # engine, so recovery does not depend on an in-memory snapshot.
        events = self.client.list_knowledge_evolution_events(
            self.access_token, limit=limit
        ) or []
        for row in events:
            current_id = row.get("iec_id")
            if current_id and selected is not None and current_id not in selected:
                continue

            event_type = str(row.get("event_type") or "").strip()
            details = row.get("details")
            if not isinstance(details, dict):
                details = {}

            engine.evolution_history.append({
                "event": event_type,
                "details": details,
                "timestamp": row.get("created_at"),
            })

            if event_type == "conflict_registered":
                conflict_id = details.get("conflict_id")
                if conflict_id:
                    engine._conflict_solver.conflicts[str(conflict_id)] = dict(details)
            elif event_type == "conflict_resolved":
                conflict_id = details.get("conflict_id")
                if conflict_id:
                    engine._conflict_solver.conflicts[str(conflict_id)] = dict(details)
            elif event_type == "evidence_merged":
                synthesis_id = details.get("synthesis_id")
                if synthesis_id:
                    engine._evidence_merger.syntheses[str(synthesis_id)] = dict(details)

        engine._conflict_solver._next_id = engine._next_numeric_id(
            engine._conflict_solver.conflicts, "CONFLICT-"
        )
        engine._evidence_merger._next_id = engine._next_numeric_id(
            engine._evidence_merger.syntheses, "SYNTHESIS-"
        )

        return engine

    def load_cycle(
        self, *, iec_ids: Optional[list[str]] = None, limit: Optional[int] = None
    ) -> Tuple[EvidenceStore, KnowledgeEvolutionEngine]:
        """Reconstruct the durable epistemic runtime after a restart."""
        store = self.load_evidence_store(limit=limit)
        engine = self.load_evolution_engine(store, iec_ids=iec_ids, limit=limit)
        return store, engine

    @staticmethod
    def _iec_id(row: Dict[str, Any]) -> Optional[str]:
        value = row.get("iec_id", row.get("id"))
        return str(value) if value is not None else None

    @classmethod
    def _iec_from_row(cls, row: Dict[str, Any]) -> IECContract:
        iec_id = cls._iec_id(row)
        if not iec_id:
            raise ValueError("Registro IEC sem identificador.")

        methodology = row.get("methodology")
        result = row.get("result")
        knowledge_type = row.get("knowledge_type")
        if not knowledge_type and isinstance(methodology, dict):
            knowledge_type = methodology.get("knowledge_type") or methodology.get("node_type")

        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        if isinstance(result, dict) and isinstance(result.get("metadata"), dict):
            metadata = {**metadata, **result["metadata"]}

        return IECContract(
            iec_id=iec_id,
            title=str(row.get("title") or row.get("name") or iec_id),
            statement=str(row.get("statement") or row.get("content") or ""),
            knowledge_type=str(knowledge_type or "unknown"),
            confidence=float(row.get("confidence") or 0.0),
            status=str(row.get("status") or "active"),
            evidence_ids=list(row.get("evidence_ids") or []),
            metadata=metadata,
            created_at=row.get("created_at") or datetime.now(UTC).isoformat(),
            updated_at=row.get("updated_at") or datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def now_iso() -> str:
        return datetime.now(UTC).isoformat()
