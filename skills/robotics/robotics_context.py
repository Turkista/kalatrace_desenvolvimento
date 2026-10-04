"""
KALATRACE Robotics Context

Defines the operational context representation
of a robotic agent connected to KALATRACE.

This object stores the current state,
environment information, sensors and mission data.
"""

from datetime import datetime, UTC


class RoboticsContext:
    """
    Represents the current context of a robot.
    """

    def __init__(self, robot_id: str):

        self.robot_id = robot_id

        self.status = "unknown"

        self.location = None

        self.mission = None

        self.sensors = {}

        self.metadata = {}

        self.updated_at = datetime.now(UTC)


    def update_status(self, status: str):
        """
        Update robot operational status.
        """

        self.status = status

        self._update_timestamp()


    def update_location(self, location: str):
        """
        Update robot location.
        """

        self.location = location

        self._update_timestamp()


    def assign_mission(self, mission: str):
        """
        Assign a mission to the robot.
        """

        self.mission = mission

        self._update_timestamp()


    def update_sensor(self, sensor_name: str, value):
        """
        Update sensor information.
        """

        self.sensors[sensor_name] = value

        self._update_timestamp()


    def add_metadata(self, key: str, value):
        """
        Add additional robot information.
        """

        self.metadata[key] = value

        self._update_timestamp()


    def to_dict(self):
        """
        Export context information.
        """

        return {
            "robot_id": self.robot_id,
            "status": self.status,
            "location": self.location,
            "mission": self.mission,
            "sensors": self.sensors,
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat()
        }


    def _update_timestamp(self):
        """
        Update last modification time.
        """

        self.updated_at = datetime.now(UTC)