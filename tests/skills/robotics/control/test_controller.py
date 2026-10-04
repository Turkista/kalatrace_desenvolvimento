"""
KALATRACE Robotics Controller Tests

Tests the base controller behavior.
"""


from skills.robotics.control.controller import Controller



def test_controller_creation():
    """
    Test controller initialization.
    """

    controller = Controller()


    assert controller.current_command is None

    assert len(controller.command_history) == 0

    assert controller.enabled is True



def test_execute_command():
    """
    Test command execution.
    """

    controller = Controller()


    command = {

        "type": "move",

        "velocity": 2
    }


    result = controller.execute(
        command
    )


    assert result["type"] == "move"

    assert result["velocity"] == 2


    assert (
        controller.current_command["velocity"]
        == 2
    )



def test_command_history():
    """
    Test command storage history.
    """

    controller = Controller()


    controller.execute(
        {
            "id": 1
        }
    )


    controller.execute(
        {
            "id": 2
        }
    )


    history = controller.get_history()


    assert len(history) == 2

    assert history[0]["id"] == 1

    assert history[1]["id"] == 2



def test_disable_controller():
    """
    Test controller disabling.
    """

    controller = Controller()


    controller.disable()


    assert controller.enabled is False



def test_execute_disabled_controller():
    """
    Test execution rejection when disabled.
    """

    controller = Controller()


    controller.disable()


    try:

        controller.execute(
            {
                "type": "move"
            }
        )

        assert False

    except RuntimeError:

        assert True



def test_enable_controller():
    """
    Test controller reactivation.
    """

    controller = Controller()


    controller.disable()

    controller.enable()


    assert controller.enabled is True



def test_controller_export():
    """
    Test controller export.
    """

    controller = Controller()


    controller.execute(
        {
            "type": "rotate"
        }
    )


    data = controller.export()


    assert data["enabled"] is True

    assert data["history_size"] == 1

    assert (
        data["current_command"]["type"]
        == "rotate"
    )



def test_controller_clear():
    """
    Test controller reset.
    """

    controller = Controller()


    controller.execute(
        {
            "type": "move"
        }
    )


    controller.clear()


    assert controller.current_command is None

    assert len(controller.command_history) == 0