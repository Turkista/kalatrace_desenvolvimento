"""
KALATRACE Robotics Pose Tests

Tests the robot pose model.
"""


from skills.robotics.localization.pose import Pose



def test_pose_creation():
    """
    Test pose creation.
    """

    pose = Pose(
        x=1.0,
        y=2.0,
        z=3.0,
        roll=0.1,
        pitch=0.2,
        yaw=0.3
    )


    assert pose.x == 1.0

    assert pose.y == 2.0

    assert pose.z == 3.0

    assert pose.roll == 0.1

    assert pose.pitch == 0.2

    assert pose.yaw == 0.3



def test_pose_update():
    """
    Test pose update.
    """

    pose = Pose()


    pose.update(
        x=10.0,
        y=20.0,
        z=5.0,
        roll=1.0,
        pitch=2.0,
        yaw=3.0
    )


    assert pose.x == 10.0

    assert pose.y == 20.0

    assert pose.z == 5.0

    assert pose.roll == 1.0

    assert pose.pitch == 2.0

    assert pose.yaw == 3.0



def test_pose_to_dict():
    """
    Test pose export.
    """

    pose = Pose(
        x=4.0,
        y=5.0,
        z=6.0
    )


    data = pose.to_dict()


    assert data["position"]["x"] == 4.0

    assert data["position"]["y"] == 5.0

    assert data["position"]["z"] == 6.0



def test_pose_default_values():
    """
    Test default pose values.
    """

    pose = Pose()


    assert pose.x == 0.0

    assert pose.y == 0.0

    assert pose.z == 0.0

    assert pose.roll == 0.0

    assert pose.pitch == 0.0

    assert pose.yaw == 0.0