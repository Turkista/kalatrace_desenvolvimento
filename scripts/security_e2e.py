#!/usr/bin/env python3
"""Disposable two-user authorization tests against the local Supabase REST/Auth APIs.

Only use with a freshly started local Supabase stack. No production URLs or keys
are accepted implicitly; all connection values must come from supabase status -o env.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("API_URL")
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("ANON_KEY")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SERVICE_ROLE_KEY")


def request(method: str, path: str, *, key: str, token: str | None = None,
            body: object | None = None, prefer: str | None = None) -> tuple[int, object | None]:
    if not BASE_URL or not key:
        raise RuntimeError("Missing local Supabase URL/API key environment variables.")
    headers = {"apikey": key, "Authorization": f"Bearer {token or key}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if prefer:
        headers["Prefer"] = prefer
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = Request(f"{BASE_URL.rstrip('/')}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read()
            status = response.status
    except HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except URLError as exc:
        raise RuntimeError(f"Local Supabase API request failed: {exc.reason}") from exc
    if not raw:
        return status, None
    try:
        return status, json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError:
        return status, raw.decode("utf-8", errors="replace")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def admin_create_user(email: str, password: str) -> dict:
    status, payload = request(
        "POST", "/auth/v1/admin/users", key=SERVICE_KEY, token=SERVICE_KEY,
        body={"email": email, "password": password, "email_confirm": True,
              "user_metadata": {"full_name": "Disposable security E2E"}},
    )
    require(status in (200, 201) and isinstance(payload, dict) and payload.get("id"),
            f"Could not create disposable test user (HTTP {status}).")
    return payload


def sign_in(email: str, password: str) -> str:
    status, payload = request(
        "POST", "/auth/v1/token?grant_type=password", key=ANON_KEY,
        body={"email": email, "password": password},
    )
    require(status == 200 and isinstance(payload, dict) and payload.get("access_token"),
            f"Could not sign in disposable test user (HTTP {status}).")
    return payload["access_token"]


def main() -> int:
    require(bool(BASE_URL and ANON_KEY and SERVICE_KEY),
            "Missing local Supabase keys. Run supabase status -o env first.")
    require("127.0.0.1" in BASE_URL or "localhost" in BASE_URL,
            "Safety stop: security_e2e.py only accepts a local Supabase URL.")

    suffix = uuid.uuid4().hex[:12]
    email_a = f"kalatrace-security-a-{suffix}@example.test"
    email_b = f"kalatrace-security-b-{suffix}@example.test"
    password_a = f"E2e-{uuid.uuid4().hex}-{uuid.uuid4().hex}!"
    password_b = f"E2e-{uuid.uuid4().hex}-{uuid.uuid4().hex}!"
    user_a = user_b = None
    passed: list[str] = []

    try:
        user_a = admin_create_user(email_a, password_a)
        user_b = admin_create_user(email_b, password_b)
        token_a = sign_in(email_a, password_a)
        token_b = sign_in(email_b, password_b)
        id_a, id_b = user_a["id"], user_b["id"]
        require(id_a != id_b, "Auth returned duplicate user IDs.")
        passed.append("two separate disposable users can authenticate through Auth")

        status, project_payload = request(
            "POST", "/rest/v1/projects", key=ANON_KEY, token=token_a,
            body={"owner_id": id_a, "slug": f"security-e2e-{suffix}",
                  "name": "Disposable security E2E project", "project_type": "scientific"},
            prefer="return=representation",
        )
        require(status in (200, 201) and isinstance(project_payload, list)
                and project_payload and project_payload[0].get("id"),
                f"Owner could not create test project (HTTP {status}).")
        project_id = project_payload[0]["id"]

        status, rows = request(
            "GET", f"/rest/v1/projects?id=eq.{project_id}&select=id",
            key=ANON_KEY, token=token_b,
        )
        require(status == 200 and rows == [],
                "Cross-user project SELECT exposed a project owned by user A.")
        passed.append("project RLS blocks cross-user reads")

        status, rows = request(
            "PATCH", f"/rest/v1/projects?id=eq.{project_id}",
            key=ANON_KEY, token=token_b,
            body={"name": "Unauthorized cross-user edit"},
            prefer="return=representation",
        )
        require(status in (200, 204) and (rows is None or rows == []),
                "Cross-user project UPDATE unexpectedly changed a row.")
        status, owner_rows = request(
            "GET", f"/rest/v1/projects?id=eq.{project_id}&select=name",
            key=ANON_KEY, token=token_a,
        )
        require(status == 200 and owner_rows and
                owner_rows[0].get("name") == "Disposable security E2E project",
                "Cross-user project UPDATE changed owner data.")
        passed.append("project RLS blocks cross-user writes")

        status, mission_payload = request(
            "POST", "/rest/v1/cmc_missions", key=ANON_KEY, token=token_a,
            body={"owner_id": id_a, "project_id": project_id,
                  "name": "Disposable security E2E mission",
                  "objective": "Verify owner isolation"},
            prefer="return=representation",
        )
        require(status in (200, 201) and isinstance(mission_payload, list)
                and mission_payload and mission_payload[0].get("id"),
                f"Owner could not create test mission (HTTP {status}).")
        mission_id = mission_payload[0]["id"]

        status, rows = request(
            "GET", f"/rest/v1/cmc_missions?id=eq.{mission_id}&select=id",
            key=ANON_KEY, token=token_b,
        )
        require(status == 200 and rows == [],
                "Cross-user CMC mission SELECT exposed user A's mission.")
        status, payload = request(
            "POST", "/rest/v1/cmc_missions", key=ANON_KEY, token=token_b,
            body={"owner_id": id_a, "project_id": project_id,
                  "name": "Forged mission", "objective": "Must be denied"},
        )
        require(status >= 400,
                "User B was able to insert a CMC mission owned by user A.")
        passed.append("CMC mission RLS blocks cross-user reads and forged ownership")

        status, payload = request(
            "PATCH", f"/rest/v1/profiles?id=eq.{id_a}",
            key=ANON_KEY, token=token_a, body={"role": "admin"},
            prefer="return=representation",
        )
        require(status >= 400,
                "Authenticated user could update their own profiles.role.")
        status, payload = request(
            "PATCH", f"/rest/v1/profiles?id=eq.{id_a}",
            key=ANON_KEY, token=token_a, body={"display_name": "Security E2E owner"},
            prefer="return=representation",
        )
        require(status in (200, 204),
                f"Allowed display_name update failed (HTTP {status}).")
        passed.append("profile role escalation denied while display_name remains editable")

        status, payload = request(
            "POST", "/rest/v1/rpc/append_cmc_mission_timeline",
            key=ANON_KEY, token=token_b,
            body={"p_mission_id": mission_id, "p_event": {"type": "unauthorized-test"}},
        )
        require(status >= 400,
                "User B could append to user A's CMC mission timeline.")
        status, payload = request(
            "POST", "/rest/v1/rpc/update_project_member_role",
            key=ANON_KEY, token=token_b,
            body={"p_project_id": project_id, "p_user_id": id_a, "p_role": "viewer"},
        )
        require(status >= 400,
                "User B could change membership roles in user A's project.")
        status, payload = request(
            "POST", "/rest/v1/rpc/get_kalatrace_infrastructure_usage",
            key=ANON_KEY, token=token_b, body={},
        )
        require(status >= 400,
                "Non-admin user could call infrastructure usage SECURITY DEFINER RPC.")
        status, payload = request(
            "POST", "/rest/v1/rpc/run_kalatrace_watchdog",
            key=ANON_KEY, token=token_b, body={},
        )
        require(status >= 400,
                "Non-admin user could run the watchdog SECURITY DEFINER RPC.")
        status, payload = request(
            "POST", "/rest/v1/rpc/record_kalatrace_watchdog_runtime",
            key=ANON_KEY, token=token_b,
            body={"p_snapshot_id": 0, "p_persistence_status": "HEALTHY",
                  "p_graph_status": "HEALTHY", "p_details": {}},
        )
        require(status >= 400,
                "Non-admin user could call watchdog runtime SECURITY DEFINER RPC.")
        passed.append("CMC/workspace/watchdog SECURITY DEFINER RPCs reject unauthorized sessions")

        print(f"PASS: {len(passed)} authorization checks")
        for item in passed:
            print(f"  - {item}")
        return 0
    finally:
        for user in (user_b, user_a):
            if user and user.get("id"):
                try:
                    request("DELETE", f"/auth/v1/admin/users/{user['id']}",
                            key=SERVICE_KEY, token=SERVICE_KEY)
                except Exception:
                    print("WARNING: failed to delete a disposable local test user", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
