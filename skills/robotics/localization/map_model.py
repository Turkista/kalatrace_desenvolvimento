"""
KALATRACE Robotics Map Model

Represents the robot's internal map of
the environment.

The map stores landmarks, obstacles and
regions that are used by localization,
navigation and planning.
"""

from copy import deepcopy
from datetime import datetime, UTC


class MapModel:
    """
    Represents the robot map.
    """

    def __init__(self):

        self.landmarks = {}

        self.obstacles = {}

        self.regions = {}

        self.metadata = {}

        self.updated_at = None

    def add_landmark(
        self,
        landmark_id: str,
        data: dict
    ):
        """
        Add or update a landmark.
        """

        self.landmarks[landmark_id] = deepcopy(data)

        self.updated_at = datetime.now(UTC)

    def remove_landmark(
        self,
        landmark_id: str
    ):
        """
        Remove a landmark.
        """

        self.landmarks.pop(
            landmark_id,
            None
        )

        self.updated_at = datetime.now(UTC)

    def add_obstacle(
        self,
        obstacle_id: str,
        data: dict
    ):
        """
        Add or update an obstacle.
        """

        self.obstacles[obstacle_id] = deepcopy(data)

        self.updated_at = datetime.now(UTC)

    def remove_obstacle(
        self,
        obstacle_id: str
    ):
        """
        Remove an obstacle.
        """

        self.obstacles.pop(
            obstacle_id,
            None
        )

        self.updated_at = datetime.now(UTC)

    def update_metadata(
        self,
        metadata: dict
    ):
        """
        Update map metadata.
        """

        self.metadata.update(
            deepcopy(metadata)
        )

        self.updated_at = datetime.now(UTC)

    def landmark_count(self):
        """
        Return the number of landmarks.
        """

        return len(self.landmarks)

    def obstacle_count(self):
        """
        Return the number of obstacles.
        """

        return len(self.obstacles)

    def clear(self):
        """
        Reset the map.
        """

        self.landmarks.clear()

        self.obstacles.clear()

        self.regions.clear()

        self.metadata.clear()

        self.updated_at = None

    def export(self):
        """
        Export the complete map.
        """

        return {

            "landmarks":
                deepcopy(self.landmarks),

            "obstacles":
                deepcopy(self.obstacles),

            "regions":
                deepcopy(self.regions),

            "metadata":
                deepcopy(self.metadata),

            "landmark_count":
                self.landmark_count(),

            "obstacle_count":
                self.obstacle_count(),

            "updated_at":
                self.updated_at.isoformat()
                if self.updated_at
                else None
        }