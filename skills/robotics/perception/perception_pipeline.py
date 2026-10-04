"""
KALATRACE Robotics Perception Pipeline

Coordinates the complete robotic perception flow.

The pipeline orchestrates the following components:

- PerceptionManager
- SensorFusion
- ObjectTracker
- EnvironmentModel

Each component is responsible for its own domain while the
pipeline coordinates the complete perception cycle.
"""

from copy import deepcopy


class PerceptionPipeline:
    """
    Coordinates the robotic perception cycle.
    """

    def __init__(
        self,
        perception_manager,
        sensor_fusion,
        object_tracker,
        environment_model,
    ):
        self.perception_manager = perception_manager
        self.sensor_fusion = sensor_fusion
        self.object_tracker = object_tracker
        self.environment_model = environment_model

    def process(self):
        """
        Execute one complete perception cycle.

        Returns a snapshot representing the robot's
        current perceptual state.
        """

        observations = self.perception_manager.get_observations()

        if self.sensor_fusion.validate():
            fusion = self.sensor_fusion.fuse()
        else:
            fusion = {
                "sensor_count": 0,
                "readings": {}
            }

        return {
            "observations": deepcopy(observations),
            "fusion": deepcopy(fusion),
            "environment": self.environment_model.export(),
            "tracked_objects": self.object_tracker.list_objects(),
        }

    def get_environment(self):
        """
        Return the current environment model.
        """
        return self.environment_model.export()

    def get_objects(self):
        """
        Return all tracked objects.
        """
        return self.object_tracker.list_objects()

    def clear(self):
        """
        Clear the runtime state of the perception pipeline.
        """

        self.sensor_fusion.clear()
        self.object_tracker.clear()
        self.environment_model.clear()

    def export(self):
        """
        Export the current perception state without
        executing a new perception cycle.
        """

        return {
            "observations": deepcopy(
                self.perception_manager.get_observations()
            ),
            "fusion": deepcopy(
                self.sensor_fusion.get_last_fusion()
            ),
            "environment": self.environment_model.export(),
            "tracked_objects": self.object_tracker.list_objects(),
        }