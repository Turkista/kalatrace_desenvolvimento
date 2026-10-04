"""
KALATRACE Robotics Skill

Core implementation of the Robotics Skill.

Responsible for managing robotic contexts,
processing robotic events and integrating
robotic agents with the KALATRACE framework.
"""


from .robotics_context import RoboticsContext

from .robotics_events import (
    RoboticsEvent,
    RobotConnected,
    RobotDisconnected,
    SensorUpdated,
    MissionStarted,
    MissionCompleted,
    ErrorDetected
)



class RoboticsSkill:
    """
    Main Robotics Skill implementation.
    """


    def __init__(self):

        self.name = "robotics"

        self.version = "1.0.0"

        self.active = False

        self.robots = {}



    def initialize(self):
        """
        Initialize the Robotics Skill.
        """

        self.active = False

        self.robots = {}



    def activate(self):
        """
        Activate the Robotics Skill.
        """

        self.active = True



    def deactivate(self):
        """
        Deactivate the Robotics Skill.
        """

        self.active = False



    def register_robot(
        self,
        robot_id: str
    ):
        """
        Register a robotic agent.
        """

        if robot_id not in self.robots:

            self.robots[robot_id] = RoboticsContext(
                robot_id
            )

        return self.robots[robot_id]



    def remove_robot(
        self,
        robot_id: str
    ):
        """
        Remove a robot from management.
        """

        if robot_id in self.robots:

            del self.robots[robot_id]



    def process_event(
        self,
        event: RoboticsEvent
    ):
        """
        Process incoming robotic events.
        """

        robot = self.register_robot(
            event.robot_id
        )


        if isinstance(event, RobotConnected):

            robot.update_status(
                "connected"
            )


        elif isinstance(event, RobotDisconnected):

            robot.update_status(
                "offline"
            )


        elif isinstance(event, SensorUpdated):

            sensor = event.data["sensor"]

            value = event.data["value"]

            robot.update_sensor(
                sensor,
                value
            )


        elif isinstance(event, MissionStarted):

            robot.assign_mission(
                event.data["mission"]
            )

            robot.update_status(
                "executing"
            )


        elif isinstance(event, MissionCompleted):

            robot.update_status(
                "completed"
            )


        elif isinstance(event, ErrorDetected):

            robot.update_status(
                "error"
            )


        return robot



    def get_robot_context(
        self,
        robot_id: str
    ):
        """
        Retrieve robot context.
        """

        return self.robots.get(
            robot_id
        )



    def get_all_robots(self):
        """
        Return all registered robots.
        """

        return self.robots



    def status(self):
        """
        Return Skill status.
        """

        return {

            "name": self.name,

            "version": self.version,

            "active": self.active,

            "robots":
                len(self.robots)

        }