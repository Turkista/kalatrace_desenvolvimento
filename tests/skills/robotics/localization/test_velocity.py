"""
KALATRACE Robotics Velocity Tests

Tests the robot velocity model.
"""


from skills.robotics.localization.velocity import Velocity



def test_velocity_creation():
    """
    Test velocity creation.
    """

    velocity = Velocity(
        linear={
            "x": 1.0,
            "y": 2.0,
            "z": 3.0
        },
        angular={
            "roll": 0.1,
            "pitch": 0.2,
            "yaw": 0.3
        }
    )


    assert velocity.linear["x"] == 1.0

    assert velocity.linear["y"] == 2.0

    assert velocity.linear["z"] == 3.0


    assert velocity.angular["yaw"] == 0.3



def test_velocity_default_values():
    """
    Test default velocity.
    """

    velocity = Velocity()


    assert velocity.linear["x"] == 0.0

    assert velocity.linear["y"] == 0.0

    assert velocity.linear["z"] == 0.0


    assert velocity.angular["roll"] == 0.0

    assert velocity.angular["pitch"] == 0.0

    assert velocity.angular["yaw"] == 0.0



def test_velocity_update():
    """
    Test velocity update.
    """

    velocity = Velocity()


    velocity.update(
        linear={
            "x": 4.0,
            "y": 5.0,
            "z": 6.0
        },
        angular={
            "roll": 1.0,
            "pitch": 2.0,
            "yaw": 3.0
        }
    )


    assert velocity.linear["x"] == 4.0

    assert velocity.linear["z"] == 6.0

    assert velocity.angular["yaw"] == 3.0



def test_velocity_stationary():
    """
    Test stationary detection.
    """

    velocity = Velocity()


    assert velocity.is_stationary()



    velocity.update(
        linear={
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        },
        angular={
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0
        }
    )


    assert not velocity.is_stationary()



def test_velocity_linear_speed():
    """
    Test linear speed calculation.
    """

    velocity = Velocity(
        linear={
            "x": 3.0,
            "y": 4.0,
            "z": 0.0
        }
    )


    speed = velocity.linear_speed()


    assert speed == 5.0



def test_velocity_to_dict():
    """
    Test velocity export.
    """

    velocity = Velocity(
        linear={
            "x": 2.0,
            "y": 0.0,
            "z": 0.0
        }
    )


    data = velocity.to_dict()


    assert data["linear"]["x"] == 2.0