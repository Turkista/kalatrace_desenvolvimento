"""
KALATRACE Robotics Environment Model Tests

Tests the EnvironmentModel responsible for
maintaining the robot's internal representation
of the surrounding world.
"""

from skills.robotics.perception.environment_model import EnvironmentModel


def create_environment():

    return EnvironmentModel()


def test_environment_creation():

    environment = create_environment()

    assert environment.object_count() == 0

    assert environment.get_robot_state() == {}

    assert environment.get_environment() == {}

    assert environment.last_update is None


def test_robot_state_update():

    environment = create_environment()

    environment.update_robot_state({

        "battery": 82,

        "status": "moving",

        "mission": "inspection"

    })

    robot = environment.get_robot_state()

    assert robot["battery"] == 82

    assert robot["status"] == "moving"

    assert robot["mission"] == "inspection"

    assert environment.last_update is not None


def test_add_object():

    environment = create_environment()

    environment.add_object(

        "person_001",

        {

            "type": "person",

            "distance": 2.3,

            "temperature": 36.7

        }

    )

    assert environment.object_count() == 1

    obj = environment.get_object("person_001")

    assert obj["type"] == "person"

    assert obj["distance"] == 2.3


def test_update_environment():

    environment = create_environment()

    environment.update_environment({

        "room_temperature": 24,

        "humidity": 60,

        "light": "normal"

    })

    data = environment.get_environment()

    assert data["room_temperature"] == 24

    assert data["humidity"] == 60

    assert data["light"] == "normal"


def test_remove_object():

    environment = create_environment()

    environment.add_object(

        "chair_001",

        {

            "type": "chair"

        }

    )

    assert environment.object_count() == 1

    environment.remove_object("chair_001")

    assert environment.object_count() == 0

    assert environment.get_object("chair_001") is None


def test_list_objects():

    environment = create_environment()

    environment.add_object(

        "person",

        {

            "type": "person"

        }

    )

    environment.add_object(

        "table",

        {

            "type": "table"

        }

    )

    objects = environment.list_objects()

    assert len(objects) == 2

    assert "person" in objects

    assert "table" in objects


def test_export_environment():

    environment = create_environment()

    environment.update_robot_state({

        "battery": 91

    })

    environment.add_object(

        "robot_target",

        {

            "type": "marker"

        }

    )

    environment.update_environment({

        "temperature": 23

    })

    exported = environment.export()

    assert exported["object_count"] == 1

    assert exported["robot_state"]["battery"] == 91

    assert exported["environment"]["temperature"] == 23

    assert exported["last_update"] is not None


def test_clear_environment():

    environment = create_environment()

    environment.update_robot_state({

        "battery": 70

    })

    environment.add_object(

        "obj",

        {

            "type": "box"

        }

    )

    environment.update_environment({

        "humidity": 50

    })

    environment.clear()

    assert environment.object_count() == 0

    assert environment.get_robot_state() == {}

    assert environment.get_environment() == {}

    assert environment.last_update is None