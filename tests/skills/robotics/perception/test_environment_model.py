"""
Tests for KALATRACE Robotics Environment Model
"""


from datetime import datetime

from skills.robotics.perception.environment_model import EnvironmentModel



def test_update_robot_state():

    model = EnvironmentModel()


    model.update_robot_state(
        {
            "position": [0, 0],
            "battery": 90,
            "mode": "navigation"
        }
    )


    state = model.get_robot_state()


    assert state["position"] == [0, 0]

    assert state["battery"] == 90

    assert state["mode"] == "navigation"


    assert isinstance(
        model.last_update,
        datetime
    )



def test_add_object():

    model = EnvironmentModel()


    model.add_object(
        "OBJ-001",
        {
            "type": "person",
            "position": [10, 5]
        }
    )


    assert model.object_count() == 1


    obj = model.get_object(
        "OBJ-001"
    )


    assert obj["type"] == "person"

    assert obj["position"] == [10, 5]



def test_remove_object():

    model = EnvironmentModel()


    model.add_object(
        "OBJ-002",
        {
            "type": "vehicle"
        }
    )


    model.remove_object(
        "OBJ-002"
    )


    assert model.object_count() == 0

    assert model.get_object(
        "OBJ-002"
    ) is None



def test_update_environment():

    model = EnvironmentModel()


    model.update_environment(
        {
            "temperature": 25,
            "lighting": "low"
        }
    )


    environment = model.get_environment()


    assert environment["temperature"] == 25

    assert environment["lighting"] == "low"



def test_list_objects():

    model = EnvironmentModel()


    model.add_object(
        "OBJ-003",
        {
            "type": "robot"
        }
    )


    objects = model.list_objects()


    assert "OBJ-003" in objects

    assert objects["OBJ-003"]["type"] == "robot"



def test_export():

    model = EnvironmentModel()


    model.update_robot_state(
        {
            "battery": 80
        }
    )


    model.add_object(
        "OBJ-004",
        {
            "type": "animal"
        }
    )


    model.update_environment(
        {
            "temperature": 20
        }
    )


    exported = model.export()


    assert exported["robot_state"]["battery"] == 80

    assert exported["objects"]["OBJ-004"]["type"] == "animal"

    assert exported["environment"]["temperature"] == 20

    assert exported["object_count"] == 1


    assert isinstance(
        exported["last_update"],
        str
    )



def test_clear():

    model = EnvironmentModel()


    model.update_robot_state(
        {
            "mode": "idle"
        }
    )


    model.add_object(
        "OBJ-005",
        {
            "type": "person"
        }
    )


    model.update_environment(
        {
            "weather": "clear"
        }
    )


    model.clear()


    assert model.robot_state == {}

    assert model.objects == {}

    assert model.environment == {}

    assert model.last_update is None