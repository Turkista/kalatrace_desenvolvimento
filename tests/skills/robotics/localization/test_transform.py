"""
KALATRACE Robotics Transform Tests

Tests the spatial transformation model.
"""


from skills.robotics.localization.transform import Transform



def test_transform_creation():
    """
    Test transform creation.
    """

    transform = Transform(
        source_frame="camera",
        target_frame="robot",
        translation={
            "x": 1.0,
            "y": 2.0,
            "z": 3.0
        },
        rotation={
            "roll": 0.1,
            "pitch": 0.2,
            "yaw": 0.3
        }
    )


    assert transform.source_frame == "camera"

    assert transform.target_frame == "robot"

    assert transform.translation["x"] == 1.0

    assert transform.rotation["yaw"] == 0.3



def test_transform_default_values():
    """
    Test default transform values.
    """

    transform = Transform(
        source_frame="world",
        target_frame="robot"
    )


    assert transform.translation["x"] == 0.0

    assert transform.translation["y"] == 0.0

    assert transform.translation["z"] == 0.0


    assert transform.rotation["roll"] == 0.0

    assert transform.rotation["pitch"] == 0.0

    assert transform.rotation["yaw"] == 0.0



def test_transform_update():
    """
    Test transform update.
    """

    transform = Transform(
        source_frame="gps",
        target_frame="robot"
    )


    transform.update(
        translation={
            "x": 5.0,
            "y": 6.0,
            "z": 7.0
        },
        rotation={
            "roll": 1.0,
            "pitch": 2.0,
            "yaw": 3.0
        }
    )


    assert transform.translation["x"] == 5.0

    assert transform.translation["z"] == 7.0

    assert transform.rotation["yaw"] == 3.0



def test_transform_identity():
    """
    Test identity transformation.
    """

    transform = Transform(
        source_frame="robot",
        target_frame="robot"
    )


    assert transform.is_identity()



def test_transform_to_dict():
    """
    Test transform export.
    """

    transform = Transform(
        source_frame="lidar",
        target_frame="robot",
        translation={
            "x": 1.0,
            "y": 0.0,
            "z": 0.5
        }
    )


    data = transform.to_dict()


    assert data["source_frame"] == "lidar"

    assert data["target_frame"] == "robot"

    assert data["translation"]["x"] == 1.0