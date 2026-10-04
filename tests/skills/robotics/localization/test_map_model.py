"""
KALATRACE Robotics Map Model Tests

Tests the robot environment map model.
"""


from skills.robotics.localization.map_model import MapModel



def test_map_creation():
    """
    Test map creation.
    """

    map_model = MapModel()


    assert map_model.landmarks == {}

    assert map_model.obstacles == {}

    assert map_model.regions == {}

    assert map_model.metadata == {}

    assert map_model.updated_at is None



def test_add_landmark():
    """
    Test landmark insertion.
    """

    map_model = MapModel()


    map_model.add_landmark(
        "landmark_001",
        {
            "type": "door",
            "position": {
                "x": 1,
                "y": 2,
                "z": 0
            }
        }
    )


    assert map_model.landmark_count() == 1

    assert (
        map_model.landmarks["landmark_001"]["type"]
        == "door"
    )



def test_remove_landmark():
    """
    Test landmark removal.
    """

    map_model = MapModel()


    map_model.add_landmark(
        "marker",
        {}
    )


    map_model.remove_landmark(
        "marker"
    )


    assert map_model.landmark_count() == 0



def test_add_obstacle():
    """
    Test obstacle insertion.
    """

    map_model = MapModel()


    map_model.add_obstacle(
        "obstacle_001",
        {
            "type": "wall"
        }
    )


    assert map_model.obstacle_count() == 1

    assert (
        map_model.obstacles["obstacle_001"]["type"]
        == "wall"
    )



def test_update_metadata():
    """
    Test metadata update.
    """

    map_model = MapModel()


    map_model.update_metadata(
        {
            "environment": "indoor"
        }
    )


    assert (
        map_model.metadata["environment"]
        == "indoor"
    )



def test_map_export():
    """
    Test map export.
    """

    map_model = MapModel()


    map_model.add_landmark(
        "tree",
        {
            "type": "vegetation"
        }
    )


    data = map_model.export()


    assert data["landmark_count"] == 1

    assert (
        data["landmarks"]["tree"]["type"]
        == "vegetation"
    )



def test_map_clear():
    """
    Test map reset.
    """

    map_model = MapModel()


    map_model.add_landmark(
        "object",
        {}
    )

    map_model.add_obstacle(
        "wall",
        {}
    )


    map_model.clear()


    assert map_model.landmark_count() == 0

    assert map_model.obstacle_count() == 0

    assert map_model.updated_at is None