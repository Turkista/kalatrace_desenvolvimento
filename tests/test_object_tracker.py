"""
KALATRACE Robotics Object Tracker Tests

Tests the ObjectTracker responsible for maintaining
the identity of perceived objects over time.
"""

import pytest

from skills.robotics.perception.object_tracker import ObjectTracker


@pytest.fixture
def tracker():
    """
    Creates a fresh object tracker.
    """
    return ObjectTracker()


def test_tracker_initialization(tracker):

    assert tracker.object_count() == 0

    assert tracker.list_objects() == {}


def test_register_object(tracker):

    tracker.register_object(

        "BOX-001",

        {

            "type": "box",

            "color": "blue"

        }

    )

    assert tracker.object_count() == 1

    obj = tracker.get_object("BOX-001")

    assert obj is not None

    assert obj["id"] == "BOX-001"

    assert obj["data"]["type"] == "box"

    assert obj["data"]["color"] == "blue"

    assert obj["observations"] == 1


def test_update_object(tracker):

    tracker.register_object(

        "BOX-001",

        {

            "type": "box"

        }

    )

    tracker.update_object(

        "BOX-001",

        {

            "type": "box",

            "status": "moving"

        }

    )

    obj = tracker.get_object("BOX-001")

    assert obj["observations"] == 2

    assert obj["data"]["status"] == "moving"


def test_update_unknown_object(tracker):

    tracker.update_object(

        "BOX-002",

        {

            "type": "crate"

        }

    )

    assert tracker.object_count() == 1

    obj = tracker.get_object("BOX-002")

    assert obj["observations"] == 1

    assert obj["data"]["type"] == "crate"


def test_contains(tracker):

    tracker.register_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    assert tracker.contains("OBJ-001")

    assert not tracker.contains("OBJ-999")


def test_remove_object(tracker):

    tracker.register_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    assert tracker.object_count() == 1

    tracker.remove_object("OBJ-001")

    assert tracker.object_count() == 0

    assert tracker.get_object("OBJ-001") is None


def test_list_objects(tracker):

    tracker.register_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    tracker.register_object(

        "OBJ-002",

        {

            "type": "table"

        }

    )

    objects = tracker.list_objects()

    assert len(objects) == 2

    assert "OBJ-001" in objects

    assert "OBJ-002" in objects


def test_clear(tracker):

    tracker.register_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    tracker.register_object(

        "OBJ-002",

        {

            "type": "table"

        }

    )

    assert tracker.object_count() == 2

    tracker.clear()

    assert tracker.object_count() == 0

    assert tracker.list_objects() == {}


def test_export(tracker):

    tracker.register_object(

        "BOX-001",

        {

            "type": "box",

            "weight": 5
        }

    )

    exported = tracker.export()

    assert "BOX-001" in exported

    assert exported["BOX-001"]["id"] == "BOX-001"

    assert exported["BOX-001"]["data"]["type"] == "box"

    assert exported["BOX-001"]["data"]["weight"] == 5

    assert exported["BOX-001"]["observations"] == 1

    assert exported["BOX-001"]["first_seen"] is not None

    assert exported["BOX-001"]["last_seen"] is not None