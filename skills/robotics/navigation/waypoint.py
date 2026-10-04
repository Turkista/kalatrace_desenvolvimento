"""
KALATRACE Robotics Navigation Waypoint

Represents a navigation target point.

A waypoint defines where the robot
should go and optional constraints.
"""


from copy import deepcopy



class Waypoint:
    """
    Represents a navigation waypoint.
    """


    def __init__(
        self,
        waypoint_id: str,
        position: dict,
        orientation: dict = None,
        tolerance: float = 0.5,
        metadata: dict = None
    ):


        self.waypoint_id = waypoint_id


        self.position = deepcopy(
            position
        )


        self.orientation = (
            deepcopy(orientation)
            if orientation
            else {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0
            }
        )


        self.tolerance = tolerance


        self.metadata = (
            deepcopy(metadata)
            if metadata
            else {}
        )



    def update_position(
        self,
        position: dict
    ):
        """
        Update waypoint position.
        """

        self.position = deepcopy(
            position
        )



    def update_orientation(
        self,
        orientation: dict
    ):
        """
        Update waypoint orientation.
        """

        self.orientation = deepcopy(
            orientation
        )



    def is_reached(
        self,
        current_position: dict,
        distance: float
    ):
        """
        Check if robot reached waypoint.
        """

        return (
            distance <= self.tolerance
        )



    def export(self):
        """
        Export waypoint state.
        """

        return {

            "waypoint_id":
                self.waypoint_id,


            "position":
                deepcopy(
                    self.position
                ),


            "orientation":
                deepcopy(
                    self.orientation
                ),


            "tolerance":
                self.tolerance,


            "metadata":
                deepcopy(
                    self.metadata
                )
        }