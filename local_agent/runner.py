from __future__ import annotations

import os
import time
from typing import Any, Callable

from .sandbox import execute_task_spec

import requests


class LocalAgentRunner:
    """Small, auditable bridge between the Local Agent process and KALATRACE API."""

    def __init__(self, api_url: str | None = None, email: str | None = None, password: str | None = None,
                 instance_name: str | None = None, poll_seconds: float | None = None) -> None:
        self.api_url = (api_url or os.getenv("KALATRACE_API_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.email = email or os.getenv("LOCAL_AGENT_EMAIL", "")
        self.password = password or os.getenv("LOCAL_AGENT_PASSWORD", "")
        self.instance_name = instance_name or os.getenv("LOCAL_AGENT_INSTANCE", "local-dev")
        self.poll_seconds = poll_seconds or float(os.getenv("LOCAL_AGENT_POLL_SECONDS", "5"))
        self.token: str | None = None
        self.instance_id: str | None = None

    def login(self) -> dict[str, Any]:
        if not self.email or not self.password:
            raise RuntimeError("Configure LOCAL_AGENT_EMAIL and LOCAL_AGENT_PASSWORD to run the local connector.")
        response = requests.post(f"{self.api_url}/auth/login", json={"email": self.email, "password": self.password}, timeout=15)
        response.raise_for_status()
        data = response.json()
        self.token = data.get("access_token")
        if not self.token:
            raise RuntimeError("Authentication succeeded without an access token.")
        return data

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self.token:
            self.login()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        response = requests.request(method, f"{self.api_url}{path}", headers=headers, timeout=15, **kwargs)
        if response.status_code == 401:
            self.login()
            headers["Authorization"] = f"Bearer {self.token}"
            response = requests.request(method, f"{self.api_url}{path}", headers=headers, timeout=15, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def heartbeat(self) -> Any:
        data = self._request("POST", "/agent/runtime/heartbeat", json={"instance_name": self.instance_name, "capabilities": ["task_polling", "test_reporting", "sandbox_execution", "controlled_code_changes"]})
        if isinstance(data, dict):
            self.instance_id = (data.get("instance") or {}).get("id")
        return data

    def claim_next(self) -> dict[str, Any] | None:
        data = self._request("POST", "/agent/runtime/claim", json={"instance_name": self.instance_name})
        return data.get("task") if isinstance(data, dict) else None

    def complete(self, task_id: str, result: dict[str, Any], status: str = "completed") -> Any:
        return self._request("POST", f"/agent/runtime/tasks/{task_id}/complete", json={"status": status, "result": result})

    def run_forever(self, handler: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> None:
        self.login()
        while True:
            try:
                self.heartbeat()
                task = self.claim_next()
                if task:
                    try:
                        if handler:
                            result = handler(task)
                        elif task.get("execution_spec"):
                            spec = task["execution_spec"]
                            result = {"sandbox": execute_task_spec(spec)}
                            # Optional post-checks make a code change a governed
                            # change+validation transaction. Failed checks can
                            # automatically restore the previous file bytes.
                            post_checks = spec.get("post_checks", []) if isinstance(spec, dict) else []
                            check_results = []
                            for check in post_checks:
                                check_result = execute_task_spec(check)
                                check_results.append(check_result)
                                if not check_result.get("ok"):
                                    result["post_checks"] = check_results
                                    if spec.get("operation") == "code_apply" and spec.get("auto_rollback", True):
                                        from .code_workspace import CodeWorkspace
                                        result["rollback"] = CodeWorkspace(root=os.getenv("LOCAL_AGENT_WORKSPACE", os.getcwd())).rollback(result["sandbox"])
                                    result["ok"] = False
                                    break
                            if post_checks and "post_checks" not in result:
                                result["post_checks"] = check_results
                            result["ok"] = bool(result.get("ok", result.get("sandbox", {}).get("ok", True)))
                        else:
                            result = {"message": "Task claimed; no execution_spec or handler configured."}
                        ok = bool(result.get("ok", True)) if isinstance(result, dict) else True
                        self.complete(task["id"], result, "completed" if ok else "failed")
                    except Exception as exc:
                        self.complete(task["id"], {"error": str(exc)}, "failed")
            except Exception:
                # Keep the process alive; the next cycle retries authentication/API access.
                pass
            time.sleep(self.poll_seconds)
