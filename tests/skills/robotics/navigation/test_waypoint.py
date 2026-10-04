"""
KALATRACE Robotics Navigation Waypoint Tests

Tests the navigation waypoint model.
"""


from skills.robotics.navigation.waypoint import Waypoint



def test_waypoint_creation():
    """
    Test waypoint creation.
    """

    waypoint = Waypoint(
        waypoint_id="wp_001",
        position={
            "x": 1,
            "y": 2,
            "z": 3
        }
    )


    assert waypoint.waypoint_id == "wp_001"

    assert waypoint.position["x"] == 1

    assert waypoint.position["y"] == 2

    assert waypoint.position["z"] == 3



def test_waypoint_default_orientation():
    """
    Test default orientation.
    """

    waypoint = Waypoint(
        waypoint_id="wp_orientation",
        position={
            "x": 0,
            "y": 0,
            "z": 0
        }
    )


    assert waypoint.orientation["roll"] == 0.0

    assert waypoint.orientation["pitch"] == 0.0

    assert waypoint.orientation["yaw"] == 0.0



def test_waypoint_custom_orientation():
    """
    Test custom orientation.
    """

    waypoint = Waypoint(
        waypoint_id="wp_rotation",
        position={
            "x": 1,
            "y": 1,
            "z": 1
        },
        orientation={
            "roll": 0.1,
            "pitch": 0.2,
            "yaw": 1.5
        }
    )


    assert waypoint.orientation["yaw"] == 1.5



def test_update_position():
    """
    Test position update.
    """

    waypoint = Waypoint(
        waypoint_id="wp_update",
        position={
            "x": 0,
            "y": 0,
            "z": 0
        }
    )


    waypoint.update_position(
        {
            "x": 10,
            "y": 20,
            "z": 30
        }
    )


    assert waypoint.position["x"] == 10

    assert waypoint.position["z"] == 30



def test_update_orientation():
    """
    Test orientation update.
    """

    waypoint = Waypoint(
        waypoint_id="wp_rotation_update",
        position={}
    )


    waypoint.update_orientation(
        {
            "roll": 1,
            "pitch": 2,
            "yaw": 3
        }
    )


    assert waypoint.orientation["yaw"] == 3



def test_waypoint_reached():
    """
    Test waypoint arrival detection.
    """

    waypoint = Waypoint(
        waypoint_id="wp_target",
        position={
            "x": 5,
            "y": 5,
            "z": 0
        },
        tolerance=1.0
    )


    assert waypoint.is_reached(
        {
            "x": 5,
            "y": 5,
            "z": 0
        },
        distance=0.5
    )


    assert not waypoint.is_reached(
        {
            "x": 5,
            "y": 5,
            "z": 0
        },
        distance=2.0
    )



def test_waypoint_export():
    """
    Test waypoint export.
    """

    waypoint = Waypoint(
        waypoint_id="wp_export",
        position={
            "x": 7,
            "y": 8,
            "z": 9
        }
    )


    data = waypoint.export()


    assert data["waypoint_id"] == "wp_export"

    assert data["position"]["x"] == 7

    assert data["tolerance"] == 0.5