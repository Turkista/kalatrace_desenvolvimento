"""
KALATRACE Robotics Object Tracker Tests

Tests the ObjectTracker responsible for
tracking perceived objects over time.
"""

from skills.robotics.perception.object_tracker import ObjectTracker


def create_tracker():

    return ObjectTracker()


def test_tracker_creation():

    tracker = create_tracker()

    assert tracker.object_count() == 0

    assert tracker.list_objects() == {}


def test_register_object():

    tracker = create_tracker()

    tracker.register_object(

        "person_001",

        {

            "type": "person",

            "position": (2.3, 1.1),

            "confidence": 0.98

        }

    )

    assert tracker.object_count() == 1

    assert tracker.exists("person_001")


def test_get_registered_object():

    tracker = create_tracker()

    tracker.register_object(

        "box_001",

        {

            "type": "box",

            "weight": 5

        }

    )

    obj = tracker.get_object("box_001")

    assert obj is not None

    assert obj["data"]["type"] == "box"

    assert obj["data"]["weight"] == 5

    assert obj["observations"] == 1


def test_update_object():

    tracker = create_tracker()

    tracker.register_object(

        "robot",

        {

            "battery": 82

        }

    )

    tracker.update_object(

        "robot",

        {

            "battery": 75

        }

    )

    obj = tracker.get_object("robot")

    assert obj["data"]["battery"] == 75

    assert obj["observations"] == 2


def test_multiple_updates():

    tracker = create_tracker()

    tracker.register_object(

        "person",

        {

            "distance": 2.5

        }

    )

    for distance in [2.4, 2.3, 2.2, 2.1]:

        tracker.update_object(

            "person",

            {

                "distance": distance

            }

        )

    obj = tracker.get_object("person")

    assert obj["data"]["distance"] == 2.1

    assert obj["observations"] == 5


def test_remove_object():

    tracker = create_tracker()

    tracker.register_object(

        "chair",

        {

            "type": "chair"

        }

    )

    assert tracker.exists("chair")

    tracker.remove_object("chair")

    assert not tracker.exists("chair")

    assert tracker.object_count() == 0


def test_list_objects():

    tracker = create_tracker()

    tracker.register_object(

        "obj1",

        {

            "type": "cube"

        }

    )

    tracker.register_object(

        "obj2",

        {

            "type": "sphere"

        }

    )

    objects = tracker.list_objects()

    assert len(objects) == 2

    assert "obj1" in objects

    assert "obj2" in objects


def test_clear_tracker():

    tracker = create_tracker()

    tracker.register_object(

        "person",

        {

            "type": "person"

        }

    )

    tracker.register_object(

        "table",

        {

            "type": "table"

        }

    )

    assert tracker.object_count() == 2

    tracker.clear()

    assert tracker.object_count() == 0

    assert tracker.list_objects() == {}


def test_unknown_object_returns_none():

    tracker = create_tracker()

    assert tracker.get_object("unknown") is None


def test_update_unknown_object_raises_error():

    tracker = create_tracker()

    try:

        tracker.update_object(

            "unknown",

            {

                "value": 10

            }

        )

        assert False

    except ValueError:

        assert True