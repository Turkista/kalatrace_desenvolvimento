from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from integrations.supabase import SupabaseError

router = APIRouter(prefix="/research/forms", tags=["Research Forms"])

FORM_TYPES = {"lote", "dose", "celular", "bruta", "toxico", "clinica", "naoconf", "relatorio"}


class ResearchFormIn(BaseModel):
    form_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "submitted"
    record_id: Optional[str] = None
    iec_id: Optional[str] = None
    knowledge_node_id: Optional[str] = None
    project_id: Optional[str] = None


@router.post("")
def create_research_form(payload: ResearchFormIn, request: Request):
    if payload.form_type not in FORM_TYPES:
        raise HTTPException(status_code=400, detail="Unknown research form type")
    if payload.status not in {"draft", "submitted", "reviewed", "archived"}:
        raise HTTPException(status_code=400, detail="Invalid research form status")
    try:
        result = request.app.state.supabase.persist_research_form(
            request.state.access_token,
            request.state.user["id"],
            payload.form_type,
            payload.data,
            payload.status,
            payload.record_id,
            payload.iec_id,
            payload.knowledge_node_id,
            payload.project_id,
        )
        return {"status": "saved", "record": result[0] if isinstance(result, list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("")
def list_research_forms(request: Request, form_type: Optional[str] = None, project_id: Optional[str] = None, limit: int = 100):
    if form_type and form_type not in FORM_TYPES:
        raise HTTPException(status_code=400, detail="Unknown research form type")
    try:
        return {"records": request.app.state.supabase.list_research_forms(request.state.access_token, form_type, limit, project_id)}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
