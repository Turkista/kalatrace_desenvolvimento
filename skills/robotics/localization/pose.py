"""
KALATRACE Robotics Pose

Represents the robot pose inside
a reference coordinate frame.

A pose contains both position
and orientation.
"""

from copy import deepcopy
from datetime import datetime, UTC


class Pose:
    """
    Represents a robot pose.
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0,
        frame_id: str = "world"
    ):

        self.x = x

        self.y = y

        self.z = z

        self.roll = roll

        self.pitch = pitch

        self.yaw = yaw

        self.frame_id = frame_id

        self.updated_at = datetime.now(UTC)

    def update(
        self,
        x: float,
        y: float,
        z: float,
        roll: float,
        pitch: float,
        yaw: float
    ):
        """
        Update the current pose.
        """

        self.x = x

        self.y = y

        self.z = z

        self.roll = roll

        self.pitch = pitch

        self.yaw = yaw

        self.updated_at = datetime.now(UTC)

    def position(self):
        """
        Return position only.
        """

        return {

            "x": self.x,

            "y": self.y,

            "z": self.z
        }

    def orientation(self):
        """
        Return orientation only.
        """

        return {

            "roll": self.roll,

            "pitch": self.pitch,

            "yaw": self.yaw
        }

    def to_dict(self):
        """
        Export pose.
        """

        return {

            "position": deepcopy(
                self.position()
            ),

            "orientation": deepcopy(
                self.orientation()
            ),

            "frame_id": self.frame_id,

            "updated_at": self.updated_at
        }