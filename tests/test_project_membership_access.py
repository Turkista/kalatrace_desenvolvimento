"""Project membership authorization regressions for KALATRACE."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from api import main as api_main


PROJECT_ID = "00000000-0000-0000-0000-000000000042"


class FakeProjectSupabase:
    def __init__(self, project=None, membership=None):
        self.project = project
        self.membership = membership
        self.calls = []

    def select(self, table, access_token, *, select="*", filters=None):
        self.calls.append((table, access_token, select, filters))
        if table == "projects":
            return [self.project] if self.project else []
        if table == "project_memberships":
            return [self.membership] if self.membership else []
        raise AssertionError(f"Unexpected table: {table}")


def request_for(user_id="user-a", token="token-a"):
    return SimpleNamespace(
        state=SimpleNamespace(
            user={"id": user_id},
            access_token=token,
        )
    )


def test_project_owner_is_authorized(monkeypatch):
    fake = FakeProjectSupabase(project={"id": PROJECT_ID, "owner_id": "user-a"})
    monkeypatch.setattr(api_main, "supabase_client", fake)

    result = api_main.require_project_access(request_for(), PROJECT_ID)

    assert result["owner_id"] == "user-a"
    assert [call[0] for call in fake.calls] == ["projects"]


def test_project_member_is_authorized_using_session_membership(monkeypatch):
    fake = FakeProjectSupabase(
        project={"id": PROJECT_ID, "owner_id": "owner"},
        membership={"project_id": PROJECT_ID, "user_id": "user-a", "role": "researcher"},
    )
    monkeypatch.setattr(api_main, "supabase_client", fake)

    result = api_main.require_project_access(request_for(), PROJECT_ID)

    assert result["membership"]["role"] == "researcher"
    assert [call[0] for call in fake.calls] == ["projects", "project_memberships"]
    assert all(call[1] == "token-a" for call in fake.calls)


def test_non_member_cannot_access_project(monkeypatch):
    fake = FakeProjectSupabase(project={"id": PROJECT_ID, "owner_id": "owner"})
    monkeypatch.setattr(api_main, "supabase_client", fake)

    with pytest.raises(HTTPException) as exc:
        api_main.require_project_access(request_for(), PROJECT_ID)

    assert exc.value.status_code == 404


def test_missing_auth_context_is_rejected_before_database_lookup(monkeypatch):
    fake = FakeProjectSupabase(project={"id": PROJECT_ID, "owner_id": "user-a"})
    monkeypatch.setattr(api_main, "supabase_client", fake)

    with pytest.raises(HTTPException) as exc:
        api_main.require_project_access(
            SimpleNamespace(state=SimpleNamespace(user={}, access_token=None)),
            PROJECT_ID,
        )

    assert exc.value.status_code == 401
    assert fake.calls == []


def test_blank_project_id_is_rejected(monkeypatch):
    fake = FakeProjectSupabase()
    monkeypatch.setattr(api_main, "supabase_client", fake)

    with pytest.raises(HTTPException) as exc:
        api_main.require_project_access(request_for(), " ")

    assert exc.value.status_code == 400
    assert fake.calls == []
