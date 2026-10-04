"""
KALATRACE Robotics Localization Manager

Coordinates the robot localization state.

The manager integrates:

- Pose
- Velocity
- Reference Frames
- Transforms
- Map Model

It provides a unified interface for
localization operations.
"""

from copy import deepcopy


class LocalizationManager:
    """
    Coordinates robot localization.
    """

    def __init__(
        self,
        pose,
        velocity,
        map_model
    ):

        self.pose = pose

        self.velocity = velocity

        self.map_model = map_model

        self.reference_frames = {}

        self.transforms = {}


    def update_pose(
        self,
        x,
        y,
        z,
        roll,
        pitch,
        yaw
    ):
        """
        Update robot pose.
        """

        self.pose.update(
            x,
            y,
            z,
            roll,
            pitch,
            yaw
        )


    def update_velocity(
        self,
        linear,
        angular
    ):
        """
        Update robot velocity.
        """

        self.velocity.update(
            linear,
            angular
        )


    def register_frame(
        self,
        frame
    ):
        """
        Register a reference frame.
        """

        self.reference_frames[
            frame.frame_id
        ] = frame


    def add_transform(
        self,
        transform
    ):
        """
        Store a transformation.
        """

        key = (

            transform.source_frame,

            transform.target_frame

        )

        self.transforms[key] = transform


    def get_pose(self):
        """
        Return current pose.
        """

        return deepcopy(
            self.pose
        )


    def get_velocity(self):
        """
        Return current velocity.
        """

        return deepcopy(
            self.velocity
        )


    def get_map(self):
        """
        Return current map.
        """

        return deepcopy(
            self.map_model
        )


    def frame_count(self):
        """
        Return number of reference frames.
        """

        return len(
            self.reference_frames
        )


    def transform_count(self):
        """
        Return number of transforms.
        """

        return len(
            self.transforms
        )


    def export(self):
        """
        Export localization state.
        """

        return {

            "pose":
                self.pose.to_dict(),

            "velocity":
                self.velocity.to_dict(),

            "map":
                self.map_model.export(),

            "reference_frames":
                {

                    key:
                        value.to_dict()

                    for key, value

                    in self.reference_frames.items()

                },

            "transforms":
                {

                    str(key):
                        value.to_dict()

                    for key, value

                    in self.transforms.items()

                }
        }


    def clear(self):
        """
        Reset localization state.
        """

        self.reference_frames.clear()

        self.transforms.clear()

        self.map_model.clear()