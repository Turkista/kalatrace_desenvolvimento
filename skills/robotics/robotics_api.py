"""
KALATRACE Robotics API

External communication layer for the
Robotics Skill.

Provides controlled access to robotic
operations and contexts.
"""


from .robotics_events import (
    RobotConnected,
    RobotDisconnected,
    SensorUpdated,
    MissionStarted,
    MissionCompleted,
    ObjectDetected,
    ErrorDetected
)



class RoboticsAPI:
    """
    External interface for Robotics Skill.
    """


    def __init__(
        self,
        robotics_skill
    ):

        self.robotics_skill = robotics_skill



    def connect_robot(
        self,
        robot_id: str,
        metadata: dict = None
    ):
        """
        Register a robot connection.
        """

        event = RobotConnected(
            robot_id,
            metadata
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def disconnect_robot(
        self,
        robot_id: str
    ):
        """
        Disconnect robot.
        """

        event = RobotDisconnected(
            robot_id
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def update_sensor(
        self,
        robot_id: str,
        sensor: str,
        value
    ):
        """
        Receive sensor data.
        """

        event = SensorUpdated(
            robot_id,
            sensor,
            value
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def start_mission(
        self,
        robot_id: str,
        mission: str
    ):
        """
        Start robot mission.
        """

        event = MissionStarted(
            robot_id,
            mission
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def complete_mission(
        self,
        robot_id: str,
        mission: str,
        result=None
    ):
        """
        Complete robot mission.
        """

        event = MissionCompleted(
            robot_id,
            mission,
            result
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def detect_object(
        self,
        robot_id: str,
        object_name: str,
        confidence: float
    ):
        """
        Register detected object.
        """

        event = ObjectDetected(
            robot_id,
            object_name,
            confidence
        )

        return event.to_dict()



    def report_error(
        self,
        robot_id: str,
        error: str
    ):
        """
        Register robot error.
        """

        event = ErrorDetected(
            robot_id,
            error
        )

        context = self.robotics_skill.process_event(
            event
        )

        return context.to_dict()



    def get_robot(
        self,
        robot_id: str
    ):
        """
        Retrieve robot state.
        """

        context = self.robotics_skill.get_robot_context(
            robot_id
        )

        if context:

            return context.to_dict()

        return None



    def get_status(self):
        """
        Return Robotics Skill status.
        """

        return self.robotics_skill.status()