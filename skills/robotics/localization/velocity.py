"""
KALATRACE Robotics Velocity

Represents the robot linear and angular
velocity.

Velocity describes how the robot moves
through space over time.
"""

from copy import deepcopy
from datetime import datetime, UTC


class Velocity:
    """
    Represents robot velocity.
    """

    def __init__(
        self,
        linear: dict = None,
        angular: dict = None
    ):

        self.linear = deepcopy(
            linear or {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.angular = deepcopy(
            angular or {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0
            }
        )

        self.updated_at = datetime.now(UTC)

    def update(
        self,
        linear: dict,
        angular: dict
    ):
        """
        Update velocity.
        """

        self.linear = deepcopy(linear)
        self.angular = deepcopy(angular)

        self.updated_at = datetime.now(UTC)

    def is_stationary(self):
        """
        Return True if the robot
        is not moving.
        """

        return (

            all(
                value == 0.0
                for value in self.linear.values()
            )

            and

            all(
                value == 0.0
                for value in self.angular.values()
            )

        )

    def linear_speed(self):
        """
        Return the linear speed magnitude.
        """

        x = self.linear["x"]
        y = self.linear["y"]
        z = self.linear["z"]

        return (
            x ** 2 +
            y ** 2 +
            z ** 2
        ) ** 0.5

    def to_dict(self):
        """
        Export velocity.
        """

        return {

            "linear":
                deepcopy(self.linear),

            "angular":
                deepcopy(self.angular),

            "updated_at":
                self.updated_at
        }