"""
KALATRACE Robotics Reference Frame Tests

Tests the reference frame model.
"""


from skills.robotics.localization.reference_frame import ReferenceFrame



def test_reference_frame_creation():
    """
    Test reference frame creation.
    """

    frame = ReferenceFrame(
        frame_id="robot",
        parent_frame="world",
        description="Robot body frame"
    )


    assert frame.frame_id == "robot"

    assert frame.parent_frame == "world"

    assert frame.description == "Robot body frame"



def test_reference_frame_without_parent():
    """
    Test root reference frame.
    """

    frame = ReferenceFrame(
        frame_id="world"
    )


    assert frame.frame_id == "world"

    assert frame.parent_frame is None



def test_reference_frame_to_dict():
    """
    Test reference frame export.
    """

    frame = ReferenceFrame(
        frame_id="camera",
        parent_frame="robot",
        description="Front camera frame"
    )


    data = frame.to_dict()


    assert data["frame_id"] == "camera"

    assert data["parent_frame"] == "robot"

    assert data["description"] == "Front camera frame"



def test_reference_frame_copy():
    """
    Test independent copy.
    """

    frame = ReferenceFrame(
        frame_id="lidar",
        parent_frame="robot"
    )


    copied = frame.copy()


    assert copied.frame_id == "lidar"

    assert copied.parent_frame == "robot"

    assert copied is not frame