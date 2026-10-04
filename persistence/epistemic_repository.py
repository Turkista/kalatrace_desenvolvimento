"""Repository for reconstructing the KALATRACE epistemic cycle from Supabase.

The repository deliberately separates durable storage from in-memory engines:
Supabase is the durable source for evidence, links, state transitions and
evolution events; EvidenceStore and KnowledgeEvolutionEngine are reconstructed
from those records after process restart.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional, Tuple

from contracts.evidence_contract import EvidenceContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import (
    KnowledgeEvolutionEngine,
)
from integrations.supabase import SupabaseClient


class EpistemicRepository:
    """Persistence boundary for the durable epistemic state."""

    def __init__(
        self,
        client: SupabaseClient,
        *,
        access_token: str,
        user_id: str,
    ) -> None:
        if not access_token:
            raise ValueError("access_token é obrigatório.")
        if not user_id:
            raise ValueError("user_id é obrigatório.")
        self.client = client
        self.access_token = access_token
        self.user_id = user_id

    def save_evidence(self, evidence: EvidenceContract) -> Any:
        evidence.validate()
        return self.client.persist_evidence(
            self.access_token,
            self.user_id,
            evidence,
        )

    def link_evidence(self, evidence_id: str, iec_id: str) -> Any:
        return self.client.link_evidence_to_iec(
            self.access_token,
            self.user_id,
            evidence_id,
            iec_id,
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
        self,
        iec_id: str,
        from_state: Optional[str],
        to_state: str,
        reason: str,
    ) -> Any:
        return self.client.record_iec_state_transition(
            self.access_token,
            self.user_id,
            iec_id,
            from_state,
            to_state,
            reason,
        )

    def record_evolution_event(
        self,
        iec_id: Optional[str],
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.client.record_knowledge_evolution_event(
            self.access_token,
            self.user_id,
            iec_id,
            event_type,
            details,
        )

    def load_evidence_store(self, *, limit: int = 500) -> EvidenceStore:
        """Rebuild EvidenceStore from durable evidence and IEC links."""
        rows = self.client.list_evidence(
            self.access_token,
            limit=limit,
        )
        store = EvidenceStore()

        for row in rows or []:
            evidence = EvidenceContract.from_dict(row)
            store.add_evidence(evidence)

        for evidence in rows or []:
            evidence_id = evidence.get("id")
            if not evidence_id:
                continue
            links = self.client.list_evidence_links_for_evidence(
                self.access_token,
                evidence_id,
                limit=limit,
            )
            for link in links or []:
                iec_id = link.get("iec_id")
                if iec_id:
                    store.link_to_iec(evidence_id, iec_id)

        return store

    def load_evolution_engine(
        self,
        evidence_store: EvidenceStore,
        *,
        iec_ids: Optional[list[str]] = None,
        limit: int = 500,
    ) -> KnowledgeEvolutionEngine:
        """Rebuild epistemic state from durable transition history."""
        engine = KnowledgeEvolutionEngine(evidence_store=evidence_store)

        target_ids = iec_ids
        if target_ids is None:
            target_ids = self._discover_iec_ids(limit=limit)

        for iec_id in target_ids:
            history = self.client.list_iec_state_history(
                self.access_token,
                iec_id,
                limit=limit,
            )
            states = [row.get("to_state") for row in history or [] if row.get("to_state")]
            if not states:
                continue

            current = states[-1]
            engine.state_manager.set_state(
                iec_id,
                current,
            )

        return engine

    def load_cycle(
        self,
        *,
        iec_ids: Optional[list[str]] = None,
        limit: int = 500,
    ) -> Tuple[EvidenceStore, KnowledgeEvolutionEngine]:
        """Reconstruct the durable epistemic runtime after a restart."""
        store = self.load_evidence_store(limit=limit)
        engine = self.load_evolution_engine(
            store,
            iec_ids=iec_ids,
            limit=limit,
        )
        return store, engine

    def _discover_iec_ids(self, *, limit: int) -> list[str]:
        """Discover IEC identifiers from durable state history."""
        rows = self.client.list_iec_state_history(
            self.access_token,
            "",
            limit=limit,
            allow_empty_iec=True,
        )
        ids: list[str] = []
        for row in rows or []:
            iec_id = row.get("iec_id")
            if iec_id and iec_id not in ids:
                ids.append(iec_id)
        return ids

    @staticmethod
    def now_iso() -> str:
        return datetime.now(UTC).isoformat()
