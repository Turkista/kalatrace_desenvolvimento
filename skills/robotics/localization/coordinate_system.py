"""
KALATRACE Robotics Coordinate System

Defines how positions are represented
inside a reference frame.

A Coordinate System describes the
mathematical convention used to express
positions and orientations.
"""

from copy import deepcopy


class CoordinateSystem:
    """
    Represents a coordinate system.
    """

    def __init__(
        self,
        system_name: str,
        dimensions: int = 3,
        units: str = "meters",
        handedness: str = "right"
    ):

        self.system_name = system_name

        self.dimensions = dimensions

        self.units = units

        self.handedness = handedness

    def is_2d(self):
        """
        Check if the system is 2D.
        """

        return self.dimensions == 2

    def is_3d(self):
        """
        Check if the system is 3D.
        """

        return self.dimensions == 3

    def to_dict(self):
        """
        Export the coordinate system.
        """

        return {

            "system_name":
                self.system_name,

            "dimensions":
                self.dimensions,

            "units":
                self.units,

            "handedness":
                self.handedness
        }

    def copy(self):
        """
        Return a copy.
        """

        return deepcopy(self)