from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class LocalAgentSandboxError(RuntimeError):
    pass


class LocalAgentSandbox:
    """Allowlisted, auditable local task executor.

    It intentionally does not execute arbitrary shell strings. Tasks must use one
    of the explicit operations below and execute inside the configured project root.
    """

    ALLOWED_OPERATIONS = {"pytest", "compileall", "node_check", "code_apply", "code_dry_run"}

    def __init__(self, root: str | None = None, timeout: int = 300) -> None:
        self.root = Path(root or os.getenv("LOCAL_AGENT_WORKSPACE", os.getcwd())).resolve()
        self.timeout = max(1, int(timeout))
        if not self.root.exists() or not self.root.is_dir():
            raise LocalAgentSandboxError(f"Workspace does not exist: {self.root}")

    def _safe_relative(self, value: str) -> Path:
        path = (self.root / value).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise LocalAgentSandboxError("Path escapes LOCAL_AGENT_WORKSPACE") from exc
        return path

    def run(self, spec: dict[str, Any]) -> dict[str, Any]:
        operation = str(spec.get("operation", "")).strip().lower()
        if operation in {"code_apply", "code_dry_run"}:
            from .code_workspace import apply_code_changes
            return apply_code_changes(spec, root=str(self.root), dry_run=operation == "code_dry_run")

        if operation not in self.ALLOWED_OPERATIONS:
            raise LocalAgentSandboxError(
                f"Unsupported operation '{operation}'. Allowed: {sorted(self.ALLOWED_OPERATIONS)}"
            )

        target = str(spec.get("target", "")).strip()
        if target:
            self._safe_relative(target)

        if operation == "pytest":
            args = [sys.executable, "-m", "pytest"]
            if target:
                args.append(target)
            args.append("-q")
        elif operation == "compileall":
            args = [sys.executable, "-m", "compileall", "-q", target or "."]
        else:
            if not target.endswith((".js", ".mjs", ".cjs")):
                raise LocalAgentSandboxError("node_check target must be a JavaScript file")
            args = ["node", "--check", target]

        env = os.environ.copy()
        env.pop("LOCAL_AGENT_PASSWORD", None)
        env.pop("SUPABASE_SERVICE_ROLE_KEY", None)

        completed = subprocess.run(
            args,
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            shell=False,
        )
        return {
            "operation": operation,
            "target": target or ".",
            "command": args,
            "returncode": completed.returncode,
            "ok": completed.returncode == 0,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-12000:],
        }


def execute_task_spec(spec: dict[str, Any], root: str | None = None) -> dict[str, Any]:
    return LocalAgentSandbox(root=root).run(spec)

