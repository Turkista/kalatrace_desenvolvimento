"""Regression tests for the Supabase-backed HTTP auth middleware.

These tests use a fake auth client and never contact the Supabase project.
"""
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from integrations.auth import install_auth_middleware
from integrations.supabase import SupabaseError


class FakeSupabaseClient:
    settings = SimpleNamespace(auth_required=True)

    def __init__(self, user=None, *, invalid=False):
        self.user = user or {"id": "user-allowed"}
        self.invalid = invalid
        self.calls = []

    def get_user(self, access_token):
        self.calls.append(access_token)
        if self.invalid:
            raise SupabaseError(401, "invalid token")
        return self.user


def make_app(client):
    app = FastAPI()
    install_auth_middleware(app, client)

    @app.get("/private")
    def private_route(request: Request):
        return {
            "user_id": request.state.user["id"],
            "token": request.state.access_token,
        }

    return app


def test_private_route_rejects_missing_bearer_token():
    supabase = FakeSupabaseClient()
    response = TestClient(make_app(supabase)).get("/private")

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_REQUIRED"
    assert supabase.calls == []


def test_private_route_rejects_invalid_or_expired_token():
    supabase = FakeSupabaseClient(invalid=True)
    response = TestClient(make_app(supabase)).get(
        "/private",
        headers={"Authorization": "Bearer expired-token"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_INVALID"
    assert supabase.calls == ["expired-token"]


def test_private_route_accepts_verified_user_and_scopes_request_context(monkeypatch):
    monkeypatch.setenv("KALATRACE_ALLOWED_USER_IDS", "user-allowed")
    supabase = FakeSupabaseClient(user={"id": "user-allowed", "email": "test@example.com"})
    response = TestClient(make_app(supabase)).get(
        "/private",
        headers={"Authorization": "Bearer valid-test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "user-allowed",
        "token": "valid-test-token",
    }
    assert supabase.calls == ["valid-test-token"]


def test_private_route_rejects_verified_user_outside_allowlist(monkeypatch):
    monkeypatch.setenv("KALATRACE_ALLOWED_USER_IDS", "another-user")
    supabase = FakeSupabaseClient(user={"id": "user-not-allowed"})
    response = TestClient(make_app(supabase)).get(
        "/private",
        headers={"Authorization": "Bearer valid-but-not-allowed"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "USER_NOT_ALLOWED"
