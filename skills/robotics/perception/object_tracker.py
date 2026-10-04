"""
KALATRACE Robotics Object Tracker

Tracks objects perceived by the robot.

The tracker maintains object identity across
multiple perception cycles.
"""

from copy import deepcopy
from datetime import datetime, timezone


class ObjectTracker:
    """
    Tracks perceived objects.
    """

    def __init__(self):

        self.objects = {}

    def register_object(
        self,
        object_id: str,
        data: dict
    ):
        """
        Register a new object.
        """

        timestamp = datetime.now(timezone.utc)

        self.objects[object_id] = {

            "id": object_id,

            "data": deepcopy(data),

            "first_seen": timestamp,

            "last_seen": timestamp,

            "observations": 1
        }

    def update_object(
        self,
        object_id: str,
        data: dict
    ):
        """
        Update an existing object.
        """

        if object_id not in self.objects:

            self.register_object(
                object_id,
                data
            )

            return

        self.objects[object_id]["data"] = deepcopy(data)

        self.objects[object_id]["last_seen"] = datetime.now(timezone.utc)

        self.objects[object_id]["observations"] += 1

    def remove_object(
        self,
        object_id: str
    ):
        """
        Remove an object from tracking.
        """

        self.objects.pop(
            object_id,
            None
        )

    def get_object(
        self,
        object_id: str
    ):
        """
        Return one tracked object.
        """

        if object_id not in self.objects:

            return None

        return deepcopy(
            self.objects[object_id]
        )

    def list_objects(self):
        """
        Return all tracked objects.
        """

        return deepcopy(
            self.objects
        )

    def contains(
        self,
        object_id: str
    ):
        """
        Check if an object is being tracked.
        """

        return object_id in self.objects

    def object_count(self):
        """
        Return the number of tracked objects.
        """

        return len(
            self.objects
        )

    def clear(self):
        """
        Remove every tracked object.
        """

        self.objects.clear()

    def export(self):
        """
        Export tracker state.
        """

        exported = {}

        for object_id, obj in self.objects.items():

            exported[object_id] = {

                "id": obj["id"],

                "data": deepcopy(obj["data"]),

                "first_seen": obj["first_seen"].isoformat(),

                "last_seen": obj["last_seen"].isoformat(),

                "observations": obj["observations"]
            }

        return exported