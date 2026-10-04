"""
KALATRACE Robotics Transform

Represents a spatial transformation
between two reference frames.

Transforms define the relative position
and orientation from one frame to another.
"""

from copy import deepcopy
from datetime import datetime, UTC


class Transform:
    """
    Represents a transformation
    between reference frames.
    """

    def __init__(
        self,
        source_frame: str,
        target_frame: str,
        translation: dict = None,
        rotation: dict = None
    ):

        self.source_frame = source_frame

        self.target_frame = target_frame

        self.translation = deepcopy(
            translation or {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.rotation = deepcopy(
            rotation or {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0
            }
        )

        self.updated_at = datetime.now(UTC)

    def update(
        self,
        translation: dict,
        rotation: dict
    ):
        """
        Update the transform.
        """

        self.translation = deepcopy(
            translation
        )

        self.rotation = deepcopy(
            rotation
        )

        self.updated_at = datetime.now(UTC)

    def is_identity(self):
        """
        Check whether this transform
        is an identity transform.
        """

        return (

            self.translation == {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }

            and

            self.rotation == {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0
            }

        )

    def to_dict(self):
        """
        Export the transform.
        """

        return {

            "source_frame":
                self.source_frame,

            "target_frame":
                self.target_frame,

            "translation":
                deepcopy(self.translation),

            "rotation":
                deepcopy(self.rotation),

            "updated_at":
                self.updated_at
        }