"""FastAPI authentication middleware backed by Supabase Auth."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request

from integrations.supabase import SupabaseClient, SupabaseError
from core.persistence.request_context import (
    set_persistence_context,
    reset_persistence_context,
)


PUBLIC_PATHS = {
    "/health",
    "/neo4j/health",
    "/neo4j/stats",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/signup",
    "/auth/login",
}


def bearer_token(request: Request) -> Optional[str]:
    value = request.headers.get("Authorization", "")
    if not value.lower().startswith("bearer "):
        return None
    token = value[7:].strip()
    return token or None


def require_user(request: Request) -> Dict[str, Any]:
    """Return the verified Supabase user or raise HTTP 401."""
    client: SupabaseClient = request.app.state.supabase
    token = bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Bearer access token required")
    try:
        user = client.get_user(token)
    except SupabaseError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
    request.state.access_token = token
    request.state.user = user
    return user


def install_auth_middleware(app, client: SupabaseClient) -> None:
    app.state.supabase = client

    @app.middleware("http")
    async def supabase_auth_middleware(request: Request, call_next):
        if not client.settings.auth_required or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = bearer_token(request)
        if not token:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required", "code": "AUTH_REQUIRED"},
            )
        try:
            user = client.get_user(token)
        except SupabaseError:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired access token", "code": "AUTH_INVALID"},
            )
        request.state.access_token = token
        request.state.user = user
        context_token = set_persistence_context(token, user["id"])
        try:
            return await call_next(request)
        finally:
            reset_persistence_context(context_token)
