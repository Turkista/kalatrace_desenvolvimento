"""
KALATRACE Robotics Environment Model Tests

Tests the EnvironmentModel responsible for maintaining
the robot's internal representation of the world.
"""

import pytest

from skills.robotics.perception.environment_model import EnvironmentModel


@pytest.fixture
def environment():
    """
    Creates a fresh environment model.
    """
    return EnvironmentModel()


def test_environment_initialization(environment):

    assert environment.object_count() == 0

    assert environment.get_robot_state() == {}

    assert environment.get_environment() == {}

    assert environment.last_update is None


def test_update_robot_state(environment):

    robot_state = {

        "position": [10, 20],

        "orientation": 90,

        "battery": 85
    }

    environment.update_robot_state(robot_state)

    exported = environment.export()

    assert exported["robot_state"]["position"] == [10, 20]

    assert exported["robot_state"]["orientation"] == 90

    assert exported["robot_state"]["battery"] == 85

    assert exported["last_update"] is not None


def test_add_object(environment):

    environment.add_object(

        "BOX-001",

        {

            "type": "box",

            "color": "blue"

        }

    )

    assert environment.object_count() == 1

    obj = environment.get_object("BOX-001")

    assert obj["type"] == "box"

    assert obj["color"] == "blue"


def test_remove_object(environment):

    environment.add_object(

        "BOX-001",

        {

            "type": "box"

        }

    )

    assert environment.object_count() == 1

    environment.remove_object("BOX-001")

    assert environment.object_count() == 0

    assert environment.get_object("BOX-001") is None


def test_update_environment(environment):

    environment.update_environment(

        {

            "temperature": 24.5,

            "lighting": "normal"

        }

    )

    env = environment.get_environment()

    assert env["temperature"] == 24.5

    assert env["lighting"] == "normal"


def test_list_objects(environment):

    environment.add_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    environment.add_object(

        "OBJ-002",

        {

            "type": "table"

        }

    )

    objects = environment.list_objects()

    assert len(objects) == 2

    assert "OBJ-001" in objects

    assert "OBJ-002" in objects


def test_clear(environment):

    environment.add_object(

        "OBJ-001",

        {

            "type": "chair"

        }

    )

    environment.update_robot_state(

        {

            "battery": 100

        }

    )

    environment.update_environment(

        {

            "temperature": 23

        }

    )

    environment.clear()

    assert environment.object_count() == 0

    assert environment.get_robot_state() == {}

    assert environment.get_environment() == {}

    assert environment.last_update is None


def test_export(environment):

    environment.add_object(

        "BOX-001",

        {

            "type": "box"

        }

    )

    environment.update_robot_state(

        {

            "battery": 92

        }

    )

    environment.update_environment(

        {

            "weather": "indoor"

        }

    )

    exported = environment.export()

    assert "robot_state" in exported

    assert "objects" in exported

    assert "environment" in exported

    assert "object_count" in exported

    assert exported["object_count"] == 1

    assert exported["objects"]["BOX-001"]["type"] == "box"

    assert exported["robot_state"]["battery"] == 92

    assert exported["environment"]["weather"] == "indoor"