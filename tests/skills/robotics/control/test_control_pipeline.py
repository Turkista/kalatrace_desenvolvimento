"""
KALATRACE Robotics Control Pipeline Tests

Tests complete control pipeline behavior.
"""


from skills.robotics.control.control_pipeline import ControlPipeline
from skills.robotics.control.control_manager import ControlManager
from skills.robotics.control.controller import Controller
from skills.robotics.control.actuator import Actuator



def create_pipeline():
    """
    Create complete control system.
    """

    manager = ControlManager()


    controller = Controller()


    actuator = Actuator(
        "motor_01"
    )


    manager.register_controller(
        "main_controller",
        controller
    )


    manager.register_actuator(
        "motor_01",
        actuator
    )


    pipeline = ControlPipeline(
        manager
    )


    return pipeline, manager, controller, actuator



def test_control_pipeline_creation():
    """
    Test pipeline initialization.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    assert pipeline.active is False

    assert pipeline.last_execution is None



def test_control_pipeline_execution():
    """
    Test complete execution cycle.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    command = {

        "type": "move",

        "speed": 5
    }


    result = pipeline.execute(
        "main_controller",
        command
    )


    assert result["type"] == "move"

    assert result["speed"] == 5


    assert pipeline.active is True


    assert (
        manager.status
        == "executing"
    )



def test_control_pipeline_state():
    """
    Test execution persistence.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    pipeline.execute(
        "main_controller",
        {
            "type": "rotate"
        }
    )


    last = pipeline.get_last_execution()


    assert last["type"] == "rotate"



def test_control_pipeline_stop():
    """
    Test pipeline stopping.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    actuator.activate(
        {
            "power": 90
        }
    )


    pipeline.stop()


    assert pipeline.active is False

    assert actuator.state == "idle"



def test_control_pipeline_export():
    """
    Test pipeline export.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    pipeline.execute(
        "main_controller",
        {
            "type": "move"
        }
    )


    data = pipeline.export()


    assert data["active"] is True

    assert (
        data["last_execution"]["type"]
        == "move"
    )


    assert (
        data["control_manager"]["status"]
        == "executing"
    )



def test_control_pipeline_clear():
    """
    Test pipeline reset.
    """

    pipeline, manager, controller, actuator = create_pipeline()


    pipeline.execute(
        "main_controller",
        {
            "type": "move"
        }
    )


    pipeline.clear()


    assert pipeline.active is False

    assert pipeline.last_execution is None

    assert (
        manager.status
        == "idle"
    )