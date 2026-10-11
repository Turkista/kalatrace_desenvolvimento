from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

import integrations.auth as auth_module
from integrations.auth import install_auth_middleware
from integrations.supabase import SupabaseError


class FakeSupabaseClient:
    settings = SimpleNamespace(auth_required=True)

    def __init__(self):
        self.calls = []

    def get_user(self, token):
        self.calls.append(token)
        return {"id": "user-allowed"}


def test_persistence_context_is_reset_after_authenticated_request(monkeypatch):
    monkeypatch.setenv("KALATRACE_ALLOWED_USER_IDS", "user-allowed")
    context_token = object()
    events = []

    monkeypatch.setattr(
        auth_module,
        "set_persistence_context",
        lambda token, user_id: events.append(("set", token, user_id)) or context_token,
    )
    monkeypatch.setattr(
        auth_module,
        "reset_persistence_context",
        lambda token: events.append(("reset", token)),
    )

    app = FastAPI()
    client = FakeSupabaseClient()
    install_auth_middleware(app, client)

    @app.get("/private")
    def private_route(request: Request):
        return {"user_id": request.state.user["id"]}

    response = TestClient(app).get(
        "/private",
        headers={"Authorization": "Bearer valid-test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-allowed"}
    assert events == [
        ("set", "valid-test-token", "user-allowed"),
        ("reset", context_token),
    ]
