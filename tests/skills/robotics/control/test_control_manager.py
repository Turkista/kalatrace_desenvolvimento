"""
KALATRACE Robotics Control Manager Tests

Tests control coordination.
"""


from skills.robotics.control.control_manager import ControlManager
from skills.robotics.control.controller import Controller
from skills.robotics.control.actuator import Actuator



def create_manager():
    """
    Create control system.
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


    return manager, controller, actuator



def test_control_manager_creation():
    """
    Test initialization.
    """

    manager = ControlManager()


    assert manager.status == "idle"

    assert len(manager.controllers) == 0

    assert len(manager.actuators) == 0



def test_register_controller():
    """
    Test controller registration.
    """

    manager = ControlManager()


    controller = Controller()


    manager.register_controller(
        "controller_01",
        controller
    )


    assert (
        "controller_01"
        in manager.controllers
    )



def test_register_actuator():
    """
    Test actuator registration.
    """

    manager = ControlManager()


    actuator = Actuator(
        "motor_01"
    )


    manager.register_actuator(
        "motor_01",
        actuator
    )


    assert (
        "motor_01"
        in manager.actuators
    )



def test_execute_command():
    """
    Test command execution.
    """

    manager, controller, actuator = create_manager()


    result = manager.execute(
        "main_controller",
        {
            "type": "move",
            "speed": 5
        }
    )


    assert result["speed"] == 5

    assert manager.status == "executing"


    assert (
        manager.last_command["speed"]
        == 5
    )



def test_stop_all_actuators():
    """
    Test stopping actuators.
    """

    manager, controller, actuator = create_manager()


    actuator.activate(
        {
            "power": 80
        }
    )


    manager.stop_all()


    assert actuator.state == "idle"

    assert manager.status == "stopped"



def test_get_last_command():
    """
    Test command retrieval.
    """

    manager, controller, actuator = create_manager()


    manager.execute(
        "main_controller",
        {
            "type": "rotate"
        }
    )


    command = manager.get_last_command()


    assert command["type"] == "rotate"



def test_control_export():
    """
    Test export.
    """

    manager, controller, actuator = create_manager()


    manager.execute(
        "main_controller",
        {
            "type": "move"
        }
    )


    data = manager.export()


    assert data["status"] == "executing"

    assert (
        "main_controller"
        in data["controllers"]
    )

    assert (
        "motor_01"
        in data["actuators"]
    )



def test_control_clear():
    """
    Test reset.
    """

    manager, controller, actuator = create_manager()


    manager.execute(
        "main_controller",
        {
            "type": "move"
        }
    )


    manager.clear()


    assert manager.status == "idle"

    assert manager.last_command is None