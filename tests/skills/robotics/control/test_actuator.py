"""
KALATRACE Robotics Actuator Tests

Tests physical actuator abstraction.
"""


from skills.robotics.control.actuator import Actuator



def test_actuator_creation():
    """
    Test actuator initialization.
    """

    actuator = Actuator(
        "motor_01"
    )


    assert actuator.actuator_id == "motor_01"

    assert actuator.state == "idle"

    assert actuator.enabled is True

    assert actuator.current_command is None



def test_activate_command():
    """
    Test actuator activation.
    """

    actuator = Actuator(
        "motor_01"
    )


    command = {

        "power": 50
    }


    result = actuator.activate(
        command
    )


    assert result["power"] == 50

    assert actuator.state == "active"

    assert (
        actuator.current_command["power"]
        == 50
    )



def test_command_history():
    """
    Test command storage.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.activate(
        {
            "power": 20
        }
    )


    actuator.activate(
        {
            "power": 80
        }
    )


    history = actuator.get_history()


    assert len(history) == 2

    assert history[0]["power"] == 20

    assert history[1]["power"] == 80



def test_stop_actuator():
    """
    Test stopping actuator.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.activate(
        {
            "power": 100
        }
    )


    actuator.stop()


    assert actuator.state == "idle"

    assert actuator.current_command is None



def test_disable_actuator():
    """
    Test actuator disabling.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.disable()


    assert actuator.enabled is False



def test_activate_disabled_actuator():
    """
    Test activation blocking.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.disable()


    try:

        actuator.activate(
            {
                "power": 50
            }
        )

        assert False


    except RuntimeError:

        assert True



def test_enable_actuator():
    """
    Test actuator reactivation.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.disable()

    actuator.enable()


    assert actuator.enabled is True



def test_actuator_export():
    """
    Test actuator export.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.activate(
        {
            "power": 60
        }
    )


    data = actuator.export()


    assert data["actuator_id"] == "motor_01"

    assert data["state"] == "active"

    assert data["history_size"] == 1

    assert (
        data["current_command"]["power"]
        == 60
    )



def test_actuator_clear():
    """
    Test actuator reset.
    """

    actuator = Actuator(
        "motor_01"
    )


    actuator.activate(
        {
            "power": 30
        }
    )


    actuator.clear()


    assert actuator.state == "idle"

    assert actuator.current_command is None

    assert len(actuator.command_history) == 0