"""
KALATRACE Robotics Navigation Route

Represents a complete navigation mission.

A route contains one or more paths
and defines a complete movement objective.
"""


from copy import deepcopy
from datetime import datetime, UTC



class Route:
    """
    Represents a navigation route.
    """


    def __init__(
        self,
        route_id: str,
        paths: list = None,
        destination: dict = None,
        metadata: dict = None
    ):

        self.route_id = route_id


        self.paths = (
            deepcopy(paths)
            if paths
            else []
        )


        self.destination = (
            deepcopy(destination)
            if destination
            else None
        )


        self.metadata = (
            deepcopy(metadata)
            if metadata
            else {}
        )


        self.created_at = datetime.now(UTC)



    def add_path(
        self,
        path
    ):
        """
        Add path to route.
        """

        self.paths.append(
            deepcopy(path)
        )



    def remove_path(
        self,
        index: int
    ):
        """
        Remove path by index.
        """

        if 0 <= index < len(self.paths):

            self.paths.pop(index)



    def path_count(self):
        """
        Return number of paths.
        """

        return len(
            self.paths
        )



    def update_destination(
        self,
        destination: dict
    ):
        """
        Update route destination.
        """

        self.destination = deepcopy(
            destination
        )



    def clear(self):
        """
        Reset route.
        """

        self.paths.clear()

        self.destination = None



    def export(self):
        """
        Export route state.
        """

        return {

            "route_id":
                self.route_id,


            "paths":
                deepcopy(
                    self.paths
                ),


            "path_count":
                self.path_count(),


            "destination":
                deepcopy(
                    self.destination
                ),


            "metadata":
                deepcopy(
                    self.metadata
                ),


            "created_at":
                self.created_at.isoformat()
        }