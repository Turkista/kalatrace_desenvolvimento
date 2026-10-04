"""
KALATRACE Robotics Environment Model

Represents the robot's current understanding
of its surrounding environment.

The Environment Model stores perceived objects,
robot state and environmental information.

This class does not perform perception.

It only maintains the current world model.
"""


from copy import deepcopy
from datetime import datetime, timezone



class EnvironmentModel:
    """
    Robot world representation.
    """


    def __init__(self):

        self.objects = {}

        self.robot_state = {}

        self.environment = {}

        self.last_update = None



    def update_robot_state(
        self,
        state: dict
    ):
        """
        Update robot internal state.
        """

        self.robot_state = deepcopy(
            state
        )

        self.last_update = datetime.now(
            timezone.utc
        )



    def add_object(
        self,
        object_id: str,
        object_data: dict
    ):
        """
        Add or update an object.
        """

        self.objects[object_id] = deepcopy(
            object_data
        )

        self.last_update = datetime.now(
            timezone.utc
        )



    def remove_object(
        self,
        object_id: str
    ):
        """
        Remove an object.
        """

        self.objects.pop(
            object_id,
            None
        )

        self.last_update = datetime.now(
            timezone.utc
        )



    def update_environment(
        self,
        data: dict
    ):
        """
        Update environment properties.
        """

        self.environment.update(
            deepcopy(data)
        )

        self.last_update = datetime.now(
            timezone.utc
        )



    def get_object(
        self,
        object_id: str
    ):
        """
        Return one object.
        """

        return deepcopy(
            self.objects.get(object_id)
        )



    def list_objects(self):
        """
        Return all objects.
        """

        return deepcopy(
            self.objects
        )



    def get_robot_state(self):
        """
        Return robot state.
        """

        return deepcopy(
            self.robot_state
        )



    def get_environment(self):
        """
        Return environment information.
        """

        return deepcopy(
            self.environment
        )



    def object_count(self):
        """
        Number of known objects.
        """

        return len(
            self.objects
        )



    def clear(self):
        """
        Reset environment.
        """

        self.objects.clear()

        self.robot_state.clear()

        self.environment.clear()

        self.last_update = None



    def export(self):
        """
        Export current world model.
        """

        return {

            "robot_state":
                deepcopy(
                    self.robot_state
                ),


            "objects":
                deepcopy(
                    self.objects
                ),


            "environment":
                deepcopy(
                    self.environment
                ),


            "object_count":
                self.object_count(),


            "last_update":
                self.last_update.isoformat()
                if self.last_update
                else None
        }