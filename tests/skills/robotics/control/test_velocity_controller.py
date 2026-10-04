"""
KALATRACE Robotics Velocity Controller Tests

Tests velocity based control.
"""


from skills.robotics.control.velocity_controller import VelocityController



def test_velocity_controller_creation():
    """
    Test initialization.
    """

    controller = VelocityController()


    velocity = controller.get_velocity()


    assert velocity["linear"] == 0

    assert velocity["angular"] == 0

    assert controller.enabled is True



def test_set_velocity():
    """
    Test velocity command generation.
    """

    controller = VelocityController()


    command = controller.set_velocity(
        linear=2.5,
        angular=0.5
    )


    assert command["type"] == "velocity"

    assert command["linear"] == 2.5

    assert command["angular"] == 0.5


    velocity = controller.get_velocity()


    assert velocity["linear"] == 2.5

    assert velocity["angular"] == 0.5



def test_velocity_history():
    """
    Test inherited command history.
    """

    controller = VelocityController()


    controller.set_velocity(
        linear=1,
        angular=0
    )


    controller.set_velocity(
        linear=3,
        angular=1
    )


    history = controller.get_history()


    assert len(history) == 2

    assert history[0]["linear"] == 1

    assert history[1]["linear"] == 3



def test_stop_velocity():
    """
    Test stopping movement.
    """

    controller = VelocityController()


    controller.set_velocity(
        linear=5,
        angular=2
    )


    command = controller.stop()


    assert command["linear"] == 0

    assert command["angular"] == 0


    velocity = controller.get_velocity()


    assert velocity["linear"] == 0

    assert velocity["angular"] == 0



def test_velocity_export():
    """
    Test exported state.
    """

    controller = VelocityController()


    controller.set_velocity(
        linear=4,
        angular=1
    )


    data = controller.export()


    assert data["enabled"] is True

    assert data["history_size"] == 1

    assert data["velocity"]["linear"] == 4

    assert data["velocity"]["angular"] == 1



def test_velocity_clear():
    """
    Test clear inherited state.
    """

    controller = VelocityController()


    controller.set_velocity(
        linear=2,
        angular=1
    )


    controller.clear()


    assert controller.current_command is None

    assert len(controller.command_history) == 0