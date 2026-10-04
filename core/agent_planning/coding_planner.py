from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from hashlib import sha256
from typing import Any, Dict, List, Optional
import json
import re


@dataclass(frozen=True)
class PlanStep:
    id: str
    action: str
    description: str
    validation: List[Dict[str, Any]]


@dataclass(frozen=True)
class CodingPlan:
    plan_id: str
    mission_id: str
    objective: str
    risk: str
    requires_approval: bool
    steps: List[PlanStep]
    execution_spec: Dict[str, Any]
    created_at: str
    planner: str = "deterministic-coding-planner"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodingPlanner:
    """Governed planner for Local Agent coding work.

    This layer creates an explicit, reviewable plan. It never approves or
    executes the plan. Execution remains behind the CMC approval boundary.
    """

    def plan(self, mission_id: str, objective: str, project_root: Optional[str] = None) -> CodingPlan:
        if not mission_id or not mission_id.strip():
            raise ValueError("mission_id cannot be empty")
        if not objective or not objective.strip():
            raise ValueError("objective cannot be empty")

        normalized = objective.strip()
        lower = normalized.lower()
        risk = "medium"
        if any(term in lower for term in ("delete", "remove", "migration", "production", "credential", "secret")):
            risk = "high"
        elif any(term in lower for term in ("test", "lint", "document", "readme", "refactor")):
            risk = "low"

        checks = [
            {"operation": "pytest", "args": ["-q"]},
            {"operation": "compileall"},
        ]

        # The planner intentionally does not invent file edits from prose.
        # A future LLM provider may propose edits, but those edits must enter
        # this same explicit execution_spec contract before approval.
        execution_spec = {
            "operation": "plan_only",
            "objective": normalized,
            "post_checks": checks,
            "auto_rollback": True,
            "workspace_root": project_root,
        }

        digest = sha256(f"{mission_id}:{normalized}".encode("utf-8")).hexdigest()[:16]
        steps = [
            PlanStep("inspect", "inspect", "Inspect project structure and relevant implementation before proposing edits.", []),
            PlanStep("design", "design", "Produce an explicit file-level change set; do not infer executable edits from prose alone.", []),
            PlanStep("validate", "validate", "Run the declared post-checks after approved code changes.", checks),
            PlanStep("evidence", "evidence", "Record execution, test output, and validation evidence for the mission.", []),
        ]
        return CodingPlan(
            plan_id=f"plan-{digest}",
            mission_id=mission_id,
            objective=normalized,
            risk=risk,
            requires_approval=True,
            steps=steps,
            execution_spec=execution_spec,
            created_at=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def validate_execution_spec(spec: Dict[str, Any]) -> None:
        if not isinstance(spec, dict):
            raise ValueError("execution_spec must be an object")
        operation = spec.get("operation")
        allowed = {"plan_only", "code_apply", "pytest", "compileall", "node_check"}
        if operation not in allowed:
            raise ValueError(f"Unsupported planner operation: {operation}")
        if operation == "code_apply":
            operations = spec.get("operations")
            if not isinstance(operations, list) or not operations:
                raise ValueError("code_apply requires explicit operations")
            for item in operations:
                if not isinstance(item, dict) or item.get("operation") not in {"create_file", "replace_text"}:
                    raise ValueError("code_apply contains an unsupported file operation")
                path = item.get("path", "")
                if not path or path.startswith("/") or ".." in path.replace("\\", "/").split("/"):
                    raise ValueError("code_apply path must stay inside the workspace")


def build_coding_plan(mission_id: str, objective: str, project_root: Optional[str] = None) -> Dict[str, Any]:
    return CodingPlanner().plan(mission_id, objective, project_root).to_dict()
