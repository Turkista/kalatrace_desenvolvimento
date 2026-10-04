"""
KALATRACE Command & Mission Center (CMC)

"Transformar objetivos estrategicos em missoes executaveis,
monitorar sua evolucao, coordenar recursos cognitivos e
garantir rastreabilidade das decisoes."

This is the single facade that unifies the four subsystems
that, until now, existed as independent packages:

    core.mission   -> Mission Manager
    core.command   -> Command Layer
    core.decision  -> Decision Oversight
    core.resource  -> Resource Allocation

The CMC itself does not implement business logic for any of
these -- it only composes them and offers mission-centric,
high-level operations that keep a Mission's commands,
decisions, and resource allocations consistent with each
other, exactly like the architecture diagram in the CMC
specification:

    USER / OPERATOR
        |
        v
    Command & Mission Center (CMC)
        |
        +--> Mission Manager
        +--> Decision Control
        +--> Resource Allocation
        |
        v
    KALATRACE ENGINES (out of scope for this facade -- see
    engines.cognitive_orchestrator.CognitiveOrchestrator for
    the actual coordination of engine execution).
"""

from __future__ import annotations

from typing import Any

from core.mission import Mission, MissionManager, MissionRegistry
from core.command import Command, CommandCenter
from core.decision import Decision, DecisionController
from core.resource import ResourceAllocation, ResourceAllocator

from .cognitive_orchestrator_bridge import CognitiveOrchestratorExecutor
from .robotics_bridge import RoboticsExecutor, executor_name_for_robot


class CommandMissionCenter:
    """
    Command & Mission Center facade.

    Composes mission lifecycle management, command
    orchestration, decision oversight, and resource
    allocation behind a single, mission-centric API.
    """

    def __init__(
        self,
        mission_manager: MissionManager | None = None,
        command_center: CommandCenter | None = None,
        decision_controller: DecisionController | None = None,
        resource_allocator: ResourceAllocator | None = None,
    ) -> None:
        """
        Initializes the Command & Mission Center.

        Every subsystem can optionally be injected, which is
        useful for tests or for sharing a subsystem across
        multiple CMC instances.
        """

        self.mission_manager = mission_manager or MissionManager(
            MissionRegistry()
        )

        self.command_center = command_center or CommandCenter()

        self.decision_controller = decision_controller or DecisionController()

        self.resource_allocator = resource_allocator or ResourceAllocator()

        self.robotics_skill: Any = None

    # =================================================
    # Internal helpers
    # =================================================

    def _get_mission(self, mission_id: str) -> Mission:

        return self.mission_manager.get_mission(mission_id)

    # =================================================
    # Mission Definition
    # =================================================

    def create_mission(
        self,
        name: str,
        objective: str,
        priority: str = "NORMAL",
        project_id: str | None = None,
    ) -> Mission:
        """
        Creates and registers a new mission.
        """

        return self.mission_manager.create_mission(
            name=name,
            objective=objective,
            priority=priority,
            project_id=project_id,
        )

    # =================================================
    # Command Layer
    # =================================================

    def issue_command(
        self,
        mission_id: str,
        name: str,
        objective: str,
        priority: str = "NORMAL",
    ) -> Command:
        """
        Creates a command tied to a mission and links it back
        onto that mission's command list, so the mission stays
        the single source of truth for what it triggered.
        """

        mission = self._get_mission(mission_id)

        command = self.command_center.create_command(
            name=name,
            objective=objective,
            mission_id=mission_id,
            priority=priority,
        )

        mission.add_command(command)

        return command

    def execute_command(
        self,
        command_id: str,
        executor: str,
    ) -> Any:
        """
        Executes a command through the Command Center.
        """

        return self.command_center.execute_command(
            command_id,
            executor,
        )

    # =================================================
    # Decision Oversight
    # =================================================

    def record_decision(
        self,
        mission_id: str,
        action: str,
        reason: str,
        confidence: float = 0.0,
        evidence: list[str] | None = None,
        alternatives: list[str] | None = None,
    ) -> Decision:
        """
        Records a decision tied to a mission and links it back
        onto that mission's decision list.
        """

        mission = self._get_mission(mission_id)

        decision = self.decision_controller.record_decision(
            action=action,
            reason=reason,
            confidence=confidence,
            mission_id=mission_id,
            evidence=evidence,
            alternatives=alternatives,
        )

        mission.add_decision(decision)

        return decision

    # =================================================
    # Resource Allocation
    # =================================================

    def allocate_resource(
        self,
        mission_id: str,
        resource_id: str,
        amount: float,
    ) -> ResourceAllocation:
        """
        Allocates resource capacity to a mission and links the
        allocation back onto that mission's resource list.
        """

        mission = self._get_mission(mission_id)

        allocation = self.resource_allocator.allocate(
            resource_id=resource_id,
            amount=amount,
            mission_id=mission_id,
        )

        mission.add_resource_allocation(allocation)

        return allocation

    def release_resource(self, allocation_id: str) -> ResourceAllocation:
        """
        Releases a resource allocation.

        The mission keeps the allocation record in its history
        for traceability; only the underlying Resource's
        available capacity is restored.
        """

        return self.resource_allocator.release(allocation_id)

    # =================================================
    # Cognitive Orchestrator Bridge
    # =================================================

    def connect_cognitive_orchestrator(
        self,
        cognitive_orchestrator: Any = None,
    ) -> CognitiveOrchestratorExecutor:
        """
        Registers the DOCUMENTO 26 Cognitive Orchestrator as a
        Command executor named "cognitive_orchestrator".

        This is opt-in: the CMC does not depend on the
        Cognitive Orchestrator (or its engine chain) unless this
        method is called. If no orchestrator instance is given,
        a new engines.cognitive_orchestrator.CognitiveOrchestrator
        is created with fresh, empty state -- pass an existing
        instance to share state (knowledge graph, evidence
        store) across the application.

        After calling this, missions can trigger a full
        cognitive cycle for a piece of knowledge via:

            cmc.issue_command(mission_id, name, objective)
            cmc.execute_command(command_id, executor="cognitive_orchestrator")

        where `objective` is used as the cycle's submission
        statement.
        """

        if cognitive_orchestrator is None:

            from engines.cognitive_orchestrator.cognitive_orchestrator_engine import (
                CognitiveOrchestrator,
            )

            cognitive_orchestrator = CognitiveOrchestrator()

        executor = CognitiveOrchestratorExecutor(cognitive_orchestrator)

        self.command_center.dispatcher.register_executor(
            executor.name,
            executor,
        )

        self.cognitive_orchestrator = cognitive_orchestrator

        return executor

    # =================================================
    # Robotics Bridge
    # =================================================

    def connect_robotics(
        self,
        robotics_skill: Any = None,
    ) -> Any:
        """
        Registers the Robotics Skill (skills.robotics) as the
        source of robots the CMC can dispatch missions to.

        This is opt-in: the CMC does not depend on the Robotics
        Skill unless this method is called. If no skill instance
        is given, a new skills.robotics.robotics_skill.RoboticsSkill
        is created with fresh, empty state -- pass an existing
        instance to share state (already-connected robots) across
        the application.

        Individual robots still need to be exposed to the Command
        Dispatcher one at a time via register_robot_executor()
        (or implicitly through send_mission_to_robot()) so that
        commands can be routed to the specific robot chosen for
        a mission.
        """

        if robotics_skill is None:

            from skills.robotics.robotics_skill import RoboticsSkill

            robotics_skill = RoboticsSkill()
            robotics_skill.activate()

        self.robotics_skill = robotics_skill

        return robotics_skill

    def _require_robotics_skill(self) -> Any:

        if self.robotics_skill is None:
            raise RuntimeError(
                "Robotics Skill is not connected. "
                "Call connect_robotics() first."
            )

        return self.robotics_skill

    def register_robot_executor(self, robot_id: str) -> RoboticsExecutor:
        """
        Registers (or re-registers) a Command executor dedicated
        to a single robot, so that mission commands can be routed
        to that specific robot by name, exactly like any other
        executor (see core.command.command_dispatcher).
        """

        robotics_skill = self._require_robotics_skill()

        executor = RoboticsExecutor(robotics_skill, robot_id)

        self.command_center.dispatcher.register_executor(
            executor.name,
            executor,
        )

        return executor

    def list_robots(self) -> dict[str, Any]:
        """
        Returns every robot currently known to the connected
        Robotics Skill, keyed by robot_id, so a caller can choose
        one before issuing a mission.
        """

        robotics_skill = self._require_robotics_skill()

        return {
            robot_id: context.to_dict()
            for robot_id, context in robotics_skill.get_all_robots().items()
        }

    def send_mission_to_robot(
        self,
        mission_id: str,
        robot_id: str,
        name: str,
        objective: str,
        priority: str = "NORMAL",
    ) -> dict[str, Any]:
        """
        Chooses a robot for an existing mission: issues a command
        tied to the mission and immediately executes it against
        that robot.

        If the robot has no dedicated executor registered yet,
        one is registered automatically (register_robot_executor
        is idempotent -- re-registering just replaces the entry).

        Returns both the created Command and the resulting
        CommandResult so callers can inspect what was dispatched
        and what the robot reported back.
        """

        robotics_skill = self._require_robotics_skill()

        if robot_id not in robotics_skill.get_all_robots():
            raise ValueError(f"Unknown robot_id: {robot_id}")

        executor_name = executor_name_for_robot(robot_id)

        if not self.command_center.dispatcher.has_executor(executor_name):
            self.register_robot_executor(robot_id)

        command = self.issue_command(
            mission_id=mission_id,
            name=name,
            objective=objective,
            priority=priority,
        )

        result = self.execute_command(
            command.command_id,
            executor=executor_name,
        )

        return {
            "command": command.to_dict(),
            "result": result.to_dict() if hasattr(result, "to_dict") else result,
        }

    # =================================================
    # Mission Overview
    # =================================================

    def mission_overview(self, mission_id: str) -> dict[str, Any]:
        """
        Returns a consolidated view of a mission: its own
        summary plus the commands, decisions, and resource
        allocations tracked by each subsystem.
        """

        mission = self._get_mission(mission_id)

        return {

            "mission": mission.summary(),

            "commands": [
                command.to_dict()
                for command in self.command_center.registry.list_all()
                if command.mission_id == mission_id
            ],

            "decisions": [
                decision.to_dict()
                for decision in self.decision_controller.list_by_mission(
                    mission_id
                )
            ],

            "resource_allocations": [
                allocation.to_dict()
                for allocation in self.resource_allocator.list_allocations_by_mission(
                    mission_id
                )
            ],

            "timeline": mission.timeline,

        }

    # =================================================
    # Observability
    # =================================================

    def stats(self) -> dict[str, Any]:
        """
        Returns aggregated status across all CMC subsystems.
        """

        return {

            "missions": self.mission_manager.registry.count(),

            "active_missions": len(
                self.mission_manager.list_active()
            ),

            "commands": self.command_center.stats(),

            "decisions": self.decision_controller.stats(),

            "resources": self.resource_allocator.stats(),

        }

    def health_check(self) -> dict[str, Any]:
        """
        Returns a lightweight operational health snapshot.
        """

        return {

            "command_mission_center": "OK",

            "command_center": self.command_center.health_check(),

            "missions": self.mission_manager.registry.count(),

            "decisions": self.decision_controller.registry.count(),

            "resources": self.resource_allocator.registry.count(),

        }

    def __repr__(self) -> str:

        return (
            f"<CommandMissionCenter "
            f"missions={self.mission_manager.registry.count()} "
            f"commands={self.command_center.registry.count()} "
            f"decisions={self.decision_controller.registry.count()} "
            f"resources={self.resource_allocator.registry.count()}>"
        )
