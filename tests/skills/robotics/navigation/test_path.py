"""
KALATRACE Robotics Navigation Path Tests

Tests the navigation path model.
"""


from skills.robotics.navigation.path import Path



def test_path_creation():
    """
    Test path creation.
    """

    path = Path(
        path_id="path_001",
        description="Main navigation route"
    )


    assert path.path_id == "path_001"

    assert path.description == "Main navigation route"

    assert path.waypoint_count() == 0



def test_add_waypoint():
    """
    Test waypoint insertion.
    """

    path = Path(
        path_id="route"
    )


    path.add_waypoint(
        {
            "x": 1,
            "y": 2,
            "z": 3
        }
    )


    assert path.waypoint_count() == 1

    assert (
        path.waypoints[0]["x"]
        == 1
    )



def test_remove_waypoint():
    """
    Test waypoint removal.
    """

    path = Path(
        path_id="route"
    )


    path.add_waypoint(
        {
            "x": 5,
            "y": 5,
            "z": 0
        }
    )


    path.remove_waypoint(
        0
    )


    assert path.waypoint_count() == 0



def test_get_waypoints_copy():
    """
    Test waypoint copy isolation.
    """

    path = Path(
        path_id="copy_test"
    )


    path.add_waypoint(
        {
            "x": 10,
            "y": 20
        }
    )


    data = path.get_waypoints()


    data[0]["x"] = 999


    assert (
        path.waypoints[0]["x"]
        == 10
    )



def test_path_export():
    """
    Test path export.
    """

    path = Path(
        path_id="export_test"
    )


    path.add_waypoint(
        {
            "x": 1,
            "y": 2
        }
    )


    data = path.export()


    assert data["path_id"] == "export_test"

    assert data["waypoint_count"] == 1

    assert (
        data["waypoints"][0]["x"]
        == 1
    )



def test_path_clear():
    """
    Test path reset.
    """

    path = Path(
        path_id="clear_test"
    )


    path.add_waypoint(
        {
            "x": 1
        }
    )


    path.clear()


    assert path.waypoint_count() == 0