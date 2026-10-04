"""
KALATRACE Robotics Localization Manager Tests

Tests localization coordination.
"""


from skills.robotics.localization.pose import Pose
from skills.robotics.localization.velocity import Velocity
from skills.robotics.localization.map_model import MapModel

from skills.robotics.localization.localization_manager import (
    LocalizationManager
)

from skills.robotics.localization.reference_frame import (
    ReferenceFrame
)

from skills.robotics.localization.transform import (
    Transform
)



def create_manager():
    """
    Helper function.
    """

    return LocalizationManager(
        pose=Pose(),
        velocity=Velocity(),
        map_model=MapModel()
    )



def test_manager_creation():
    """
    Test manager initialization.
    """

    manager = create_manager()


    assert manager.pose is not None

    assert manager.velocity is not None

    assert manager.map_model is not None

    assert manager.frame_count() == 0

    assert manager.transform_count() == 0



def test_update_pose():
    """
    Test pose update through manager.
    """

    manager = create_manager()


    manager.update_pose(
        x=10,
        y=20,
        z=5,
        roll=0,
        pitch=0,
        yaw=1
    )


    pose = manager.get_pose()


    assert pose.x == 10

    assert pose.y == 20

    assert pose.z == 5

    assert pose.yaw == 1



def test_update_velocity():
    """
    Test velocity update.
    """

    manager = create_manager()


    manager.update_velocity(
        linear={
            "x": 2,
            "y": 0,
            "z": 0
        },
        angular={
            "roll": 0,
            "pitch": 0,
            "yaw": 0
        }
    )


    velocity = manager.get_velocity()


    assert velocity.linear["x"] == 2



def test_register_reference_frame():
    """
    Test frame registration.
    """

    manager = create_manager()


    frame = ReferenceFrame(
        frame_id="robot",
        parent_frame="world"
    )


    manager.register_frame(
        frame
    )


    assert manager.frame_count() == 1

    assert (
        manager.reference_frames["robot"]
        .parent_frame
        == "world"
    )



def test_add_transform():
    """
    Test transform registration.
    """

    manager = create_manager()


    transform = Transform(
        source_frame="camera",
        target_frame="robot"
    )


    manager.add_transform(
        transform
    )


    assert manager.transform_count() == 1



def test_export():
    """
    Test localization export.
    """

    manager = create_manager()


    data = manager.export()


    assert "pose" in data

    assert "velocity" in data

    assert "map" in data

    assert "reference_frames" in data

    assert "transforms" in data



def test_clear():
    """
    Test manager reset.
    """

    manager = create_manager()


    manager.register_frame(
        ReferenceFrame(
            frame_id="robot"
        )
    )


    manager.add_transform(
        Transform(
            source_frame="camera",
            target_frame="robot"
        )
    )


    manager.clear()


    assert manager.frame_count() == 0

    assert manager.transform_count() == 0