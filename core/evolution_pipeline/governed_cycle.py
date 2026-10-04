from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, Optional

from core.agent_planning.coding_planner import CodingPlanner


class GovernedEvolutionCycle:
    """Formal bridge from mission intent to a governed coding task.

    It creates a proposal only. Human approval is a separate state transition
    and the Local Agent is the only component allowed to execute the approved
    specification.
    """

    def __init__(self, planner: Optional[CodingPlanner] = None) -> None:
        self.planner = planner or CodingPlanner()

    def propose(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        mission_id = str(mission.get("id") or mission.get("mission_id") or "").strip()
        objective = str(mission.get("objective") or "").strip()
        if not mission_id or not objective:
            raise ValueError("mission id and objective are required")
        plan = self.planner.plan(mission_id, objective, mission.get("project_root"))
        return {
            "event": "agent_plan_proposed",
            "at": datetime.now(UTC).isoformat(),
            "mission_id": mission_id,
            "plan": plan.to_dict(),
            "next_state": "planning",
            "approval_required": True,
        }
