"""
KALATRACE Robotics Reference Frame

Represents a reference frame used by
robotic localization and navigation.

Reference frames define how positions,
orientations and transformations are
interpreted inside the system.
"""

from copy import deepcopy


class ReferenceFrame:
    """
    Represents a reference frame.
    """

    def __init__(
        self,
        frame_id: str,
        parent_frame: str = None,
        description: str = None
    ):

        self.frame_id = frame_id

        self.parent_frame = parent_frame

        self.description = description

    def to_dict(self):
        """
        Export frame information.
        """

        return {

            "frame_id":
                self.frame_id,

            "parent_frame":
                self.parent_frame,

            "description":
                self.description
        }

    def copy(self):
        """
        Return a copy of this frame.
        """

        return deepcopy(self)