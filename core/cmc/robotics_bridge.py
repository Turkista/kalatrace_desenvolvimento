"""
KALATRACE CMC <-> Robotics Bridge

Connects the Command & Mission Center's Command Layer to the
existing skills.robotics.robotics_skill.RoboticsSkill, using the
same CommandExecutor contract already used by the Cognitive
Orchestrator bridge (see core.cmc.cognitive_orchestrator_bridge
and core.command.command_dispatcher.CommandDispatcher: "Executors
may represent: Agents, Engines, Skills, External workers").

Design note -- one executor per robot
--------------------------------------
CommandDispatcher.dispatch(command, target) routes purely by an
executor *name* string; Command itself has no robot_id field and
this module deliberately does not add one to the core Command
entity. Instead, each robot gets its own executor registered
under the name "robotics:{robot_id}". Choosing which robot a
mission's command goes to is therefore just choosing which
executor name to execute with -- exactly the mechanism the
dispatcher already provides, no core entity changes required.

This module does not implement robotic behavior. It only adapts
Command <-> RoboticsSkill events, exactly like the Cognitive
Orchestrator bridge adapts Command <-> CognitiveOrchestrator.
"""

from __future__ import annotations

from typing import Any

from core.command.command import Command
from core.command.command_executor import CommandExecutor
from core.command.command_result import CommandResult


def executor_name_for_robot(robot_id: str) -> str:
    """
    Builds the deterministic executor name used to route
    commands to a specific robot.
    """

    if not isinstance(robot_id, str) or not robot_id.strip():
        raise ValueError("robot_id cannot be empty.")

    return f"robotics:{robot_id.strip()}"


class RoboticsExecutor(CommandExecutor):
    """
    Adapts a single robot, managed by a RoboticsSkill instance,
    to the CommandExecutor contract.

    Command.objective is used as the mission name/description
    sent to the robot (RoboticsAPI.start_mission). The resulting
    robot context is wrapped into a CommandResult so the CMC
    keeps a uniform result shape regardless of which executor
    actually ran the command.
    """

    def __init__(
        self,
        robotics_skill: Any,
        robot_id: str,
    ) -> None:
        """
        Wraps one robot inside a RoboticsSkill instance.

        The skill is injected rather than constructed here,
        since RoboticsSkill owns real state (all registered
        robots) that should be created once and shared across
        every RoboticsExecutor, not re-created per robot.
        """

        if robotics_skill is None:
            raise ValueError("robotics_skill cannot be None.")

        if not hasattr(robotics_skill, "process_event"):
            raise TypeError(
                "robotics_skill must implement process_event()."
            )

        if not isinstance(robot_id, str) or not robot_id.strip():
            raise ValueError("robot_id cannot be empty.")

        self.robotics_skill = robotics_skill

        self.robot_id = robot_id.strip()

    @property
    def name(self) -> str:
        """
        Executor identifier used for registration and routing.
        """

        return executor_name_for_robot(self.robot_id)

    def execute(self, command: Command) -> CommandResult:
        """
        Starts a mission on this executor's robot using the
        command's objective as the mission description, and
        returns the outcome as a CommandResult.
        """

        if not isinstance(command, Command):
            raise TypeError(
                "execute() requires a Command instance."
            )

        from skills.robotics.robotics_events import MissionStarted

        try:

            event = MissionStarted(
                self.robot_id,
                command.objective,
            )

            context = self.robotics_skill.process_event(event)

        except Exception as exc:

            return CommandResult.failure_result(
                command_id=command.command_id,
                message=f"Robot mission dispatch failed: {exc}",
                executor=self.name,
            )

        return CommandResult.success_result(
            command_id=command.command_id,
            message=(
                f"Mission '{command.objective}' started on "
                f"robot {self.robot_id}."
            ),
            data=context.to_dict(),
            executor=self.name,
        )

    def __repr__(self) -> str:

        return f"<RoboticsExecutor robot_id={self.robot_id!r}>"
