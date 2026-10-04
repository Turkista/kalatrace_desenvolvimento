"""
KALATRACE Robotics Localization Pipeline

Coordinates the complete localization cycle.

The pipeline integrates:

- LocalizationManager

and exposes the current
robot localization state.
"""

from copy import deepcopy


class LocalizationPipeline:
    """
    Coordinates localization flow.
    """

    def __init__(
        self,
        localization_manager
    ):

        self.localization_manager = (
            localization_manager
        )


    def process(self):
        """
        Execute one localization cycle.

        Returns the current localization
        snapshot.
        """

        return {

            "pose":
                deepcopy(
                    self.localization_manager
                    .get_pose()
                    .to_dict()
                ),

            "velocity":
                deepcopy(
                    self.localization_manager
                    .get_velocity()
                    .to_dict()
                ),

            "map":
                deepcopy(
                    self.localization_manager
                    .get_map()
                    .export()
                )
        }


    def get_pose(self):
        """
        Return current robot pose.
        """

        return (
            self.localization_manager
            .get_pose()
        )


    def get_velocity(self):
        """
        Return current velocity.
        """

        return (
            self.localization_manager
            .get_velocity()
        )


    def get_map(self):
        """
        Return current map.
        """

        return (
            self.localization_manager
            .get_map()
        )


    def export(self):
        """
        Export localization state.
        """

        return deepcopy(
            self.localization_manager
            .export()
        )


    def clear(self):
        """
        Reset localization.
        """

        self.localization_manager.clear()