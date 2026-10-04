"""
KALATRACE Robotics Localization Integration Tests

Tests complete localization workflow.
"""


from skills.robotics.localization.pose import Pose

from skills.robotics.localization.velocity import (
    Velocity
)

from skills.robotics.localization.map_model import (
    MapModel
)

from skills.robotics.localization.reference_frame import (
    ReferenceFrame
)

from skills.robotics.localization.transform import (
    Transform
)

from skills.robotics.localization.localization_manager import (
    LocalizationManager
)

from skills.robotics.localization.localization_pipeline import (
    LocalizationPipeline
)



def create_system():
    """
    Create complete localization system.
    """

    manager = LocalizationManager(
        pose=Pose(),
        velocity=Velocity(),
        map_model=MapModel()
    )


    pipeline = LocalizationPipeline(
        manager
    )


    return manager, pipeline



def test_complete_localization_cycle():
    """
    Test complete localization flow.
    """

    manager, pipeline = create_system()


    manager.update_pose(
        x=10,
        y=20,
        z=5,
        roll=0,
        pitch=0,
        yaw=1.57
    )


    manager.update_velocity(
        linear={
            "x": 2,
            "y": 0,
            "z": 0
        },
        angular={
            "roll": 0,
            "pitch": 0,
            "yaw": 0.1
        }
    )


    manager.map_model.add_landmark(
        "target",
        {
            "type": "marker"
        }
    )


    snapshot = pipeline.process()


    assert snapshot["pose"]["position"]["x"] == 10

    assert snapshot["velocity"]["linear"]["x"] == 2

    assert (
        snapshot["map"]["landmark_count"]
        == 1
    )



def test_localization_reference_chain():
    """
    Test coordinate reference chain.
    """

    manager, pipeline = create_system()


    manager.register_frame(
        ReferenceFrame(
            frame_id="world"
        )
    )


    manager.register_frame(
        ReferenceFrame(
            frame_id="robot",
            parent_frame="world"
        )
    )


    manager.add_transform(
        Transform(
            source_frame="robot",
            target_frame="world"
        )
    )


    data = pipeline.export()


    assert (
        len(data["reference_frames"])
        == 2
    )


    assert (
        len(data["transforms"])
        == 1
    )



def test_localization_clear_cycle():
    """
    Test complete reset.
    """

    manager, pipeline = create_system()


    manager.update_pose(
        x=5,
        y=5,
        z=5,
        roll=0,
        pitch=0,
        yaw=0
)


    manager.map_model.add_landmark(
        "object",
        {}
    )


    pipeline.clear()


    data = pipeline.export()


    assert (
        data["map"]["landmark_count"]
        == 0
    )


    assert (
        len(data["reference_frames"])
        == 0
    )


    assert (
        len(data["transforms"])
        == 0
    )