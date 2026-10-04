"""
KALATRACE Robotics Navigation Path

Represents a planned navigation path.

A path is a sequence of waypoints
that a robot or drone can follow.
"""


from copy import deepcopy
from datetime import datetime, UTC



class Path:
    """
    Represents a navigation path.
    """


    def __init__(
        self,
        path_id: str,
        waypoints: list = None,
        description: str = None
    ):

        self.path_id = path_id

        self.waypoints = (
            deepcopy(waypoints)
            if waypoints
            else []
        )

        self.description = description

        self.created_at = datetime.now(UTC)



    def add_waypoint(
        self,
        waypoint
    ):
        """
        Add a waypoint to the path.
        """

        self.waypoints.append(
            deepcopy(waypoint)
        )



    def remove_waypoint(
        self,
        index: int
    ):
        """
        Remove waypoint by index.
        """

        if 0 <= index < len(self.waypoints):

            self.waypoints.pop(index)



    def waypoint_count(self):
        """
        Return number of waypoints.
        """

        return len(
            self.waypoints
        )



    def clear(self):
        """
        Remove all waypoints.
        """

        self.waypoints.clear()



    def get_waypoints(self):
        """
        Return path waypoints.
        """

        return deepcopy(
            self.waypoints
        )



    def export(self):
        """
        Export path state.
        """

        return {

            "path_id":
                self.path_id,

            "waypoints":
                deepcopy(
                    self.waypoints
                ),

            "waypoint_count":
                self.waypoint_count(),

            "description":
                self.description,

            "created_at":
                self.created_at.isoformat()
        }