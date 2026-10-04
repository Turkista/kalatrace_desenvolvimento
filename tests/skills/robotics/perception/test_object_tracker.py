"""
Tests for KALATRACE Robotics Object Tracker
"""


from datetime import datetime

from skills.robotics.perception.object_tracker import ObjectTracker



def test_register_object():

    tracker = ObjectTracker()

    tracker.register_object(
        "OBJ-001",
        {
            "type": "person",
            "position": [10, 5]
        }
    )


    assert tracker.contains(
        "OBJ-001"
    )


    obj = tracker.get_object(
        "OBJ-001"
    )


    assert obj["id"] == "OBJ-001"

    assert obj["data"]["type"] == "person"

    assert obj["data"]["position"] == [10, 5]

    assert obj["observations"] == 1


    assert isinstance(
        obj["first_seen"],
        datetime
    )


    assert isinstance(
        obj["last_seen"],
        datetime
    )



def test_update_object():

    tracker = ObjectTracker()


    tracker.register_object(
        "OBJ-002",
        {
            "type": "robot",
            "position": [0, 0]
        }
    )


    tracker.update_object(
        "OBJ-002",
        {
            "type": "robot",
            "position": [5, 5]
        }
    )


    obj = tracker.get_object(
        "OBJ-002"
    )


    assert obj["data"]["position"] == [5, 5]

    assert obj["observations"] == 2



def test_update_unknown_object_creates_object():

    tracker = ObjectTracker()


    tracker.update_object(
        "OBJ-003",
        {
            "type": "vehicle"
        }
    )


    assert tracker.contains(
        "OBJ-003"
    )


    obj = tracker.get_object(
        "OBJ-003"
    )


    assert obj["observations"] == 1



def test_remove_object():

    tracker = ObjectTracker()


    tracker.register_object(
        "OBJ-004",
        {
            "type": "animal"
        }
    )


    tracker.remove_object(
        "OBJ-004"
    )


    assert not tracker.contains(
        "OBJ-004"
    )


    assert tracker.get_object(
        "OBJ-004"
    ) is None



def test_object_count():

    tracker = ObjectTracker()


    tracker.register_object(
        "OBJ-005",
        {}
    )


    tracker.register_object(
        "OBJ-006",
        {}
    )


    assert tracker.object_count() == 2



def test_export():

    tracker = ObjectTracker()


    tracker.register_object(
        "OBJ-007",
        {
            "type": "camera"
        }
    )


    exported = tracker.export()


    assert "OBJ-007" in exported


    assert exported["OBJ-007"]["id"] == "OBJ-007"


    assert exported["OBJ-007"]["data"]["type"] == "camera"


    assert isinstance(
        exported["OBJ-007"]["first_seen"],
        str
    )


    assert isinstance(
        exported["OBJ-007"]["last_seen"],
        str
    )