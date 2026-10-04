from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CodeWorkspaceError(RuntimeError):
    """Raised when a local-agent code change violates workspace policy."""


class CodeWorkspace:
    """Controlled file-change layer for the Local Agent.

    This is deliberately not an arbitrary shell/file API. A task must provide
    explicit, bounded file operations. Every changed file is backed up before
    mutation and a machine-readable audit record is returned.
    """

    MAX_FILE_BYTES = 512_000
    MAX_TOTAL_BYTES = 2_000_000
    MAX_OPERATIONS = 25
    ALLOWED_ACTIONS = {"create_file", "replace_text"}

    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or ".").resolve()
        if not self.root.is_dir():
            raise CodeWorkspaceError(f"Workspace does not exist: {self.root}")

    def _safe_path(self, value: str) -> Path:
        if not value or "\\" in value:
            raise CodeWorkspaceError("Path must be a non-empty POSIX-relative path")
        path = (self.root / value).resolve()
        try:
            path.relative_to(self.root)
        except ValueError as exc:
            raise CodeWorkspaceError("Path escapes LOCAL_AGENT_WORKSPACE") from exc
        if path == self.root:
            raise CodeWorkspaceError("Workspace root is not a file target")
        return path

    @staticmethod
    def _sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _backup(self, path: Path, old: bytes) -> str:
        rel = path.relative_to(self.root)
        backup = self.root / ".kalatrace_agent" / "backups" / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = backup.with_name(f"{backup.name}.{stamp}.bak")
        backup.write_bytes(old)
        return backup.relative_to(self.root).as_posix()

    def apply(self, spec: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
        operations = spec.get("operations")
        if not isinstance(operations, list) or not operations:
            raise CodeWorkspaceError("code_apply requires a non-empty operations list")
        if len(operations) > self.MAX_OPERATIONS:
            raise CodeWorkspaceError(f"Maximum of {self.MAX_OPERATIONS} file operations exceeded")

        total = 0
        changes: list[dict[str, Any]] = []
        staged: list[tuple[Path, bytes, bytes, str]] = []

        for index, operation in enumerate(operations):
            if not isinstance(operation, dict):
                raise CodeWorkspaceError(f"Operation {index} must be an object")
            action = str(operation.get("action", "")).strip().lower()
            if action not in self.ALLOWED_ACTIONS:
                raise CodeWorkspaceError(f"Unsupported code action: {action}")
            path = self._safe_path(str(operation.get("path", "")))
            old = path.read_bytes() if path.exists() else b""
            if path.exists() and not path.is_file():
                raise CodeWorkspaceError(f"Target is not a file: {operation.get('path')}")
            if len(old) > self.MAX_FILE_BYTES:
                raise CodeWorkspaceError(f"Existing file is too large: {operation.get('path')}")

            if action == "create_file":
                if path.exists() and not operation.get("overwrite", False):
                    raise CodeWorkspaceError(f"File already exists; set overwrite=true explicitly: {operation.get('path')}")
                content = operation.get("content")
                if not isinstance(content, str):
                    raise CodeWorkspaceError("create_file requires string content")
                new = content.encode("utf-8")
            else:
                old_text = operation.get("old_text")
                new_text = operation.get("new_text")
                if not isinstance(old_text, str) or not isinstance(new_text, str):
                    raise CodeWorkspaceError("replace_text requires old_text and new_text strings")
                text = old.decode("utf-8")
                occurrences = text.count(old_text)
                if occurrences != 1:
                    raise CodeWorkspaceError(
                        f"replace_text requires exactly one match in {operation.get('path')}; found {occurrences}"
                    )
                new = text.replace(old_text, new_text, 1).encode("utf-8")

            if len(new) > self.MAX_FILE_BYTES:
                raise CodeWorkspaceError(f"Resulting file is too large: {operation.get('path')}")
            total += len(new)
            if total > self.MAX_TOTAL_BYTES:
                raise CodeWorkspaceError("Total code-change payload exceeds safety limit")
            staged.append((path, old, new, action))
            changes.append({
                "path": str(path.relative_to(self.root)),
                "action": action,
                "before_sha256": self._sha256(old) if path.exists() else None,
                "after_sha256": self._sha256(new),
                "bytes_after": len(new),
            })

        if dry_run:
            return {"ok": True, "dry_run": True, "changes": changes}

        applied: list[dict[str, Any]] = []
        try:
            for path, old, new, action in staged:
                backup = self._backup(path, old) if path.exists() else None
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(new)
                item = next(x for x in changes if x["path"] == str(path.relative_to(self.root)) and x["action"] == action)
                item["backup"] = backup
                applied.append(item)
        except Exception:
            # Best-effort rollback for files already changed in this transaction.
            for path, old, _, _ in staged[: len(applied)]:
                if old:
                    path.write_bytes(old)
                elif path.exists():
                    path.unlink()
            raise

        audit = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "root": str(self.root),
            "changes": applied,
        }
        audit_path = self.root / ".kalatrace_agent" / "audit"
        audit_path.mkdir(parents=True, exist_ok=True)
        audit_file = audit_path / f"change-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json"
        audit_file.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "dry_run": False, "changes": applied, "audit_file": str(audit_file.relative_to(self.root))}

    def rollback(self, result: dict[str, Any]) -> dict[str, Any]:
        """Restore the exact pre-change bytes recorded by an apply result."""
        restored = []
        for change in reversed(result.get("changes", [])):
            path = self._safe_path(change["path"])
            backup = change.get("backup")
            if backup:
                backup_path = self._safe_path(backup)
                path.write_bytes(backup_path.read_bytes())
                restored.append(change["path"])
            elif path.exists():
                path.unlink()
                restored.append(change["path"])
        return {"ok": True, "restored": restored}


def apply_code_changes(spec: dict[str, Any], root: str | None = None, dry_run: bool = False) -> dict[str, Any]:
    return CodeWorkspace(root=root).apply(spec, dry_run=dry_run)
