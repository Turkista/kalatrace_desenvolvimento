"""Supabase Auth + Data API integration for the local KALATRACE backend.

The local API never uses a service-role/secret key.  Requests to the Data API
carry the authenticated user's access token, so PostgreSQL RLS remains the
final authorization boundary.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class SupabaseSettings:
    url: str
    publishable_key: str
    auth_required: bool = True
    timeout_seconds: float = 15.0

    @classmethod
    def from_env(cls) -> "SupabaseSettings":
        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be configured."
            )
        return cls(
            url=url,
            publishable_key=key,
            auth_required=os.getenv("KALATRACE_AUTH_REQUIRED", "true").lower()
            not in {"0", "false", "no", "off"},
            timeout_seconds=float(os.getenv("SUPABASE_TIMEOUT_SECONDS", "15")),
        )


class SupabaseError(RuntimeError):
    def __init__(self, status_code: int, message: str, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class SupabaseClient:
    def __init__(self, settings: Optional[SupabaseSettings] = None):
        self.settings = settings or SupabaseSettings.from_env()

    def _headers(self, access_token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "apikey": self.settings.publishable_key,
            "Content-Type": "application/json",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    @staticmethod
    def _json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    def _request(self, method: str, path: str, *, access_token: Optional[str] = None,
                 json: Any = None, params: Optional[Dict[str, str]] = None,
                 prefer: Optional[str] = None) -> Any:
        headers = self._headers(access_token)
        if prefer:
            headers["Prefer"] = prefer
        response = requests.request(
            method,
            f"{self.settings.url}{path}",
            headers=headers,
            json=json,
            params=params,
            timeout=self.settings.timeout_seconds,
        )
        payload = self._json(response)
        if not response.ok:
            message = payload.get("msg") if isinstance(payload, dict) else None
            message = message or payload.get("message") if isinstance(payload, dict) else message
            raise SupabaseError(response.status_code, message or "Supabase request failed", payload)
        return payload

    # ---------------- Auth ----------------
    def get_user(self, access_token: str) -> Dict[str, Any]:
        return self._request("GET", "/auth/v1/user", access_token=access_token)

    def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/auth/v1/signup",
            json={"email": email, "password": password, "data": metadata or {}},
        )

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/auth/v1/token",
            params={"grant_type": "password"},
            json={"email": email, "password": password},
        )

    def sign_out(self, access_token: str) -> None:
        self._request("POST", "/auth/v1/logout", access_token=access_token)

    # ---------------- Data API ----------------

    def rpc(self, function_name: str, access_token: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        return self._request(
            "POST",
            f"/rest/v1/rpc/{function_name}",
            access_token=access_token,
            json=payload or {},
        )
    def insert(self, table: str, row: Dict[str, Any], access_token: str) -> Any:
        return self._request(
            "POST",
            f"/rest/v1/{table}",
            access_token=access_token,
            json=row,
            prefer="return=representation",
        )

    def upsert(self, table: str, row: Dict[str, Any], access_token: str,
               on_conflict: str = "id") -> Any:
        return self._request(
            "POST",
            f"/rest/v1/{table}",
            access_token=access_token,
            json=row,
            params={"on_conflict": on_conflict},
            prefer="resolution=merge-duplicates,return=representation",
        )

    def select(self, table: str, access_token: str, *, select: str = "*",
               filters: Optional[Dict[str, str]] = None) -> Any:
        return self._request(
            "GET",
            f"/rest/v1/{table}",
            access_token=access_token,
            params={"select": select, **(filters or {})},
        )

    def delete(self, table: str, access_token: str, filters: Dict[str, str]) -> Any:
        return self._request(
            "DELETE",
            f"/rest/v1/{table}",
            access_token=access_token,
            params=filters,
            prefer="return=representation",
        )


    def _select_all_pages(
        self,
        table: str,
        access_token: str,
        *,
        filters: Optional[Dict[str, str]] = None,
        page_size: int = 500,
        max_rows: Optional[int] = None,
    ) -> Any:
        """Lê uma coleção ordenada sem truncar silenciosamente em 500 registros."""
        page_size = min(max(int(page_size), 1), 500)
        collected = []
        offset = 0
        base_filters = dict(filters or {})
        base_filters.pop("limit", None)
        base_filters.pop("offset", None)
        while True:
            remaining = None if max_rows is None else max_rows - len(collected)
            if remaining is not None and remaining <= 0:
                break
            current_size = page_size if remaining is None else min(page_size, remaining)
            rows = self.select(
                table,
                access_token,
                filters={**base_filters, "limit": str(current_size), "offset": str(offset)},
            )
            rows = rows if isinstance(rows, list) else []
            collected.extend(rows)
            if len(rows) < current_size:
                break
            offset += len(rows)
        return collected

    def persist_iec(self, access_token: str, user_id: str, iec: Any) -> Any:
        """Persiste uma IEC sem confundir iec_id com o campo legado id."""
        iec_id = getattr(iec, "iec_id", getattr(iec, "id", None))
        statement = getattr(iec, "statement", getattr(iec, "content", ""))
        knowledge_type = getattr(iec, "knowledge_type", getattr(iec, "node_type", "unknown"))
        if not iec_id:
            raise ValueError("IEC deve possuir iec_id.")
        return self.upsert(
            "iecs",
            {
                "id": iec_id,
                "owner_id": user_id,
                "name": iec_id,
                "statement": statement,
                "methodology": {"knowledge_type": knowledge_type},
                "result": {
                    "metadata": getattr(iec, "metadata", {}) or {},
                    "confidence": getattr(iec, "confidence", 0.0),
                    "status": getattr(iec, "status", "active"),
                    "evidence_ids": getattr(iec, "evidence_ids", []) or [],
                },
            },
            access_token,
        )


    def persist_research_form(self, access_token: str, user_id: str, form_type: str, data: Dict[str, Any], status: str = "submitted", record_id: Optional[str] = None, iec_id: Optional[str] = None, knowledge_node_id: Optional[str] = None, project_id: Optional[str] = None) -> Any:
        row = {
            "owner_id": user_id,
            "form_type": form_type,
            "status": status,
            "data": data,
            "source": "frontend",
        }
        if record_id:
            row["id"] = record_id
        if project_id:
            row["project_id"] = project_id
        if iec_id:
            row["iec_id"] = iec_id
        if knowledge_node_id:
            row["knowledge_node_id"] = knowledge_node_id
        result = self.upsert("research_form_records", row, access_token)
        created = result[0] if isinstance(result, list) and result else result
        if isinstance(created, dict) and created.get("id"):
            self.insert("research_form_record_events", {
                "record_id": created["id"],
                "owner_id": user_id,
                "event_type": "submitted",
                "payload": {"form_type": form_type},
            }, access_token)
        return result

    def list_research_forms(self, access_token: str, form_type: Optional[str] = None, limit: int = 100, project_id: Optional[str] = None) -> Any:
        filters = {"order": "created_at.desc", "limit": str(min(max(limit, 1), 500))}
        if form_type:
            filters["form_type"] = f"eq.{form_type}"
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        return self.select("research_form_records", access_token, filters=filters)

    def get_iec(self, access_token: str, iec_id: str) -> Any:
        return self.select("iecs", access_token, filters={"id": f"eq.{iec_id}", "limit": "1"})

    def upsert_knowledge_sync_status(self, access_token: str, user_id: str, iec_id: str, knowledge_node_id: str, status: str, attempts: int, last_error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Any:
        return self.upsert("knowledge_sync_status", {
            "owner_id": user_id,
            "iec_id": iec_id,
            "knowledge_node_id": knowledge_node_id,
            "target": "neo4j",
            "status": status,
            "attempts": attempts,
            "last_error": last_error,
            "last_synced_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat() if status == "synced" else None,
            "metadata": metadata or {},
        }, access_token, on_conflict="owner_id,iec_id,target")

    def list_knowledge_sync_status(self, access_token: str, iec_id: Optional[str] = None, limit: int = 100) -> Any:
        filters = {"order": "updated_at.desc", "limit": str(min(max(limit, 1), 500))}
        if iec_id:
            filters["iec_id"] = f"eq.{iec_id}"
        return self.select("knowledge_sync_status", access_token, filters=filters)

    def list_projects(self, access_token: str, limit: int = 100) -> Any:
        return self.select("projects", access_token, filters={"order": "created_at.asc", "limit": str(min(max(limit, 1), 500))})

    def create_project(self, access_token: str, user_id: str, data: Dict[str, Any]) -> Any:
        row = {**data, "owner_id": user_id}
        result = self.insert("projects", row, access_token)
        project = result[0] if isinstance(result, list) and result else result
        if isinstance(project, dict) and project.get("id"):
            self.upsert("project_memberships", {"project_id": project["id"], "user_id": user_id, "role": "owner"}, access_token)
        return result

    def update_project(self, access_token: str, project_id: str, values: Dict[str, Any]) -> Any:
        return self._request("PATCH", "/rest/v1/projects", access_token=access_token, json=values, params={"id": f"eq.{project_id}"}, prefer="return=representation")

    def delete_project(self, access_token: str, project_id: str) -> Any:
        return self._request("DELETE", "/rest/v1/projects", access_token=access_token, params={"id": f"eq.{project_id}"}, prefer="return=representation")

    def list_project_memberships(self, access_token: str, project_id: Optional[str] = None) -> Any:
        filters = {"order": "created_at.asc", "limit": "500"}
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        return self.select("project_memberships", access_token, filters=filters)

    def create_cmc_mission(self, access_token: str, user_id: str, data: Dict[str, Any]) -> Any:
        return self.insert("cmc_missions", {**data, "owner_id": user_id}, access_token)

    def list_cmc_missions(self, access_token: str, project_id: Optional[str] = None, limit: int = 100) -> Any:
        filters = {"order": "created_at.desc", "limit": str(min(max(limit, 1), 500))}
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        return self.select("cmc_missions", access_token, filters=filters)

    def append_cmc_mission_timeline(self, access_token: str, mission_id: str, event: Dict[str, Any]) -> Any:
        return self.rpc("append_cmc_mission_timeline", access_token, {"p_mission_id": mission_id, "p_event": event})

    def persist_agent_task(self, access_token: str, user_id: str, project_id: str, title: str, description: str = "", priority: int = 50, task_type: str = "improvement", execution_spec: Optional[Dict[str, Any]] = None, *, mission_id: Optional[str] = None, plan: Optional[Dict[str, Any]] = None) -> Any:
        row = {"owner_id": user_id, "project_id": project_id, "title": title, "description": description, "priority": priority, "task_type": task_type, "requested_by": "frontend", "status": "queued", "execution_spec": execution_spec or {}, "plan": plan or {}}
        if mission_id:
            row["mission_id"] = mission_id
        return self.insert("local_agent_tasks", row, access_token)

    def claim_next_agent_task(self, access_token: str, instance_name: str) -> Any:
        return self.rpc("claim_next_local_agent_task", access_token, {"p_instance_name": instance_name})

    def list_agent_tasks(self, access_token: str, project_id: Optional[str] = None, limit: int = 100) -> Any:
        filters = {"order": "priority.desc,created_at.desc", "limit": str(min(max(limit, 1), 500))}
        if project_id: filters["project_id"] = f"eq.{project_id}"
        return self.select("local_agent_tasks", access_token, filters=filters)

    def update_agent_task(self, access_token: str, task_id: str, values: Dict[str, Any]) -> Any:
        return self._request("PATCH", "/rest/v1/local_agent_tasks", access_token=access_token, json=values, params={"id": f"eq.{task_id}"}, prefer="return=representation")

    def persist_evidence(self, access_token: str, user_id: str, evidence: Any) -> Any:
        """Persiste uma EvidenceContract sem promover confiança a verdade científica."""
        return self.upsert(
            "evidence",
            {
                "id": evidence.id,
                "owner_id": user_id,
                "evidence_type": evidence.evidence_type,
                "source": evidence.source,
                "title": evidence.title,
                "content": evidence.description,
                "confidence": evidence.confidence,
                "quality_score": evidence.quality_score,
                "evidence_level": evidence.evidence_level,
                "doi": evidence.doi,
                "pmid": evidence.pmid,
                "url": evidence.url,
                "domain": evidence.domain,
                "category": evidence.category,
                "version": evidence.version,
                "metadata": evidence.metadata or {},
            },
            access_token,
        )

    def list_evidence(
        self,
        access_token: str,
        *,
        evidence_id: Optional[str] = None,
        limit: Optional[int] = 100,
    ) -> Any:
        filters = {"order": "created_at.asc"}
        if evidence_id:
            filters["id"] = f"eq.{evidence_id}"
        return self._select_all_pages("evidence", access_token, filters=filters, max_rows=limit)

    def link_evidence_to_iec(
        self,
        access_token: str,
        user_id: str,
        evidence_id: str,
        iec_id: str,
        relation: str = "SUPPORTS",
        weight: float = 1.0,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Persiste o vínculo epistemológico Evidence -> IEC."""
        return self.upsert(
            "evidence_iec_links",
            {
                "evidence_id": evidence_id,
                "iec_id": iec_id,
                "owner_id": user_id,
                "relation": relation,
                "weight": weight,
                "reason": reason,
                "metadata": metadata or {},
            },
            access_token,
            on_conflict="evidence_id,iec_id",
        )

    def list_evidence_iec_links(
        self,
        access_token: str,
        *,
        iec_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        limit: Optional[int] = 500,
    ) -> Any:
        filters = {"order": "created_at.asc"}
        if iec_id:
            filters["iec_id"] = f"eq.{iec_id}"
        if evidence_id:
            filters["evidence_id"] = f"eq.{evidence_id}"
        return self._select_all_pages("evidence_iec_links", access_token, filters=filters, max_rows=limit)

    def list_evidence_for_iec(
        self,
        access_token: str,
        iec_id: str,
        limit: int = 100,
    ) -> Any:
        return self.select(
            "evidence_iec_links",
            access_token,
            filters={
                "iec_id": f"eq.{iec_id}",
                "order": "created_at.asc",
                "limit": str(min(max(limit, 1), 500)),
            },
        )

    def record_evidence_history(
        self,
        access_token: str,
        user_id: str,
        evidence_id: str,
        event_type: str,
        *,
        previous_confidence: Optional[float] = None,
        new_confidence: Optional[float] = None,
        reason: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.insert(
            "evidence_history",
            {
                "evidence_id": evidence_id,
                "owner_id": user_id,
                "event_type": event_type,
                "previous_confidence": previous_confidence,
                "new_confidence": new_confidence,
                "reason": reason,
                "payload": payload or {},
            },
            access_token,
        )

    def record_iec_state_transition(
        self,
        access_token: str,
        user_id: str,
        iec_id: str,
        from_state: Optional[str],
        to_state: str,
        reason: str,
    ) -> Any:
        return self.insert(
            "iec_state_history",
            {
                "iec_id": iec_id,
                "owner_id": user_id,
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
            },
            access_token,
        )

    def record_knowledge_evolution_event(
        self,
        access_token: str,
        user_id: str,
        iec_id: Optional[str],
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return self.insert(
            "knowledge_evolution_events",
            {
                "iec_id": iec_id,
                "owner_id": user_id,
                "event_type": event_type,
                "details": details or {},
            },
            access_token,
        )

    def list_iec_state_history(
        self,
        access_token: str,
        iec_id: str,
        limit: int = 500,
    ) -> Any:
        return self.select(
            "iec_state_history",
            access_token,
            filters={
                "iec_id": f"eq.{iec_id}",
                "order": "created_at.asc",
                "limit": str(min(max(limit, 1), 500)),
            },
        )

    def list_all_iec_state_history(self, access_token: str, limit: Optional[int] = 500) -> Any:
        return self._select_all_pages(
            "iec_state_history", access_token,
            filters={"order": "created_at.asc"}, max_rows=limit,
        )

    def list_knowledge_evolution_events(
        self,
        access_token: str,
        *,
        iec_id: Optional[str] = None,
        limit: Optional[int] = 500,
    ) -> Any:
        filters = {"order": "created_at.asc"}
        if iec_id:
            filters["iec_id"] = f"eq.{iec_id}"
        return self._select_all_pages("knowledge_evolution_events", access_token, filters=filters, max_rows=limit)

    def list_iecs(self, access_token: str, limit: Optional[int] = 500) -> Any:
        return self._select_all_pages(
            "iecs", access_token,
            filters={"order": "created_at.asc"}, max_rows=limit,
        )

    def list_project_invitations(self, access_token: str, project_id: Optional[str] = None) -> Any:
        filters = {"order": "created_at.desc", "limit": "500"}
        if project_id:
            filters["project_id"] = f"eq.{project_id}"
        return self.select("project_invitations", access_token, filters=filters)

    def update_project_member_role(self, access_token: str, project_id: str, user_id: str, role: str) -> Any:
        return self.rpc("update_project_member_role", access_token, {"p_project_id": project_id, "p_user_id": user_id, "p_role": role})

    def remove_project_member(self, access_token: str, project_id: str, user_id: str) -> Any:
        return self.delete("project_memberships", access_token, {"project_id": f"eq.{project_id}", "user_id": f"eq.{user_id}"})

    def create_project_invitation(self, access_token: str, user_id: str, project_id: str, email: str, role: str) -> Any:
        return self.insert("project_invitations", {"project_id": project_id, "email": email.strip().lower(), "role": role, "invited_by": user_id}, access_token)

    def revoke_project_invitation(self, access_token: str, invitation_id: str) -> Any:
        return self._request("PATCH", "/rest/v1/project_invitations", access_token=access_token, json={"status": "revoked", "updated_at": "now()"}, params={"id": f"eq.{invitation_id}"}, prefer="return=representation")

    def list_project_templates(self, access_token: str) -> Any:
        return self.select("project_templates", access_token, filters={"active": "eq.true", "order": "name.asc"})

    def list_cmc_artifacts(self, table: str, access_token: str, mission_id: str, limit: int = 100) -> Any:
        return self.select(table, access_token, filters={"mission_id": f"eq.{mission_id}", "order": "created_at.desc", "limit": str(min(max(limit,1),500))})

    def persist_cmc_artifact(self, table: str, access_token: str, user_id: str, row: Dict[str, Any]) -> Any:
        return self.insert(table, {**row, "owner_id": user_id}, access_token)

    def list_agent_instances(self, access_token: str) -> Any:
        return self.select("local_agent_instances", access_token, filters={"order":"updated_at.desc","limit":"100"})

    def upsert_agent_instance(self, access_token: str, user_id: str, instance_name: str, capabilities: list[str]) -> Any:
        return self.upsert("local_agent_instances", {"instance_name": instance_name, "owner_id": user_id, "status": "online", "capabilities": capabilities, "last_heartbeat_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}, access_token, on_conflict="instance_name")

    def persist_cmc_command(self, access_token: str, user_id: str, command: Any) -> Any:
        return self.upsert("cmc_commands", {"id": command.command_id, "mission_id": command.mission_id, "owner_id": user_id, "name": command.name, "objective": command.objective, "priority": command.priority, "status": getattr(command.status, "value", str(command.status)), "executor": None, "result": {}}, access_token)

    def persist_cmc_decision(self, access_token: str, user_id: str, decision: Any) -> Any:
        return self.upsert("cmc_decisions", {"id": decision.decision_id, "mission_id": decision.mission_id, "owner_id": user_id, "action": decision.action, "reason": decision.reason, "confidence": decision.confidence, "evidence": decision.evidence, "alternatives": decision.alternatives, "status": getattr(decision.status, "value", str(decision.status))}, access_token)

    def persist_cmc_resource(self, access_token: str, user_id: str, allocation: Any) -> Any:
        return self.upsert("cmc_resource_allocations", {"id": allocation.allocation_id, "mission_id": allocation.mission_id, "owner_id": user_id, "resource_id": allocation.resource_id, "amount": allocation.amount, "status": getattr(allocation.status, "value", str(allocation.status))}, access_token)
