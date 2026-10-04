"""
KALATRACE Robotics Localization Pipeline Tests

Tests localization orchestration.
"""


from skills.robotics.localization.pose import Pose
from skills.robotics.localization.velocity import Velocity
from skills.robotics.localization.map_model import MapModel

from skills.robotics.localization.localization_manager import (
    LocalizationManager
)

from skills.robotics.localization.localization_pipeline import (
    LocalizationPipeline
)



def create_pipeline():
    """
    Create localization pipeline.
    """

    manager = LocalizationManager(
        pose=Pose(),
        velocity=Velocity(),
        map_model=MapModel()
    )


    return LocalizationPipeline(
        manager
    )



def test_pipeline_creation():
    """
    Test pipeline creation.
    """

    pipeline = create_pipeline()


    assert pipeline.localization_manager is not None



def test_pipeline_process():
    """
    Test localization cycle.
    """

    pipeline = create_pipeline()


    data = pipeline.process()


    assert "pose" in data

    assert "velocity" in data

    assert "map" in data



def test_pipeline_get_pose():
    """
    Test pose retrieval.
    """

    pipeline = create_pipeline()


    pose = pipeline.get_pose()


    assert pose.x == 0.0

    assert pose.y == 0.0

    assert pose.z == 0.0



def test_pipeline_get_velocity():
    """
    Test velocity retrieval.
    """

    pipeline = create_pipeline()


    velocity = pipeline.get_velocity()


    assert velocity.linear["x"] == 0.0



def test_pipeline_export():
    """
    Test pipeline export.
    """

    pipeline = create_pipeline()


    data = pipeline.export()


    assert "pose" in data

    assert "velocity" in data

    assert "map" in data



def test_pipeline_clear():
    """
    Test pipeline reset.
    """

    pipeline = create_pipeline()


    pipeline.clear()


    data = pipeline.export()


    assert data["pose"] is not None

    assert data["velocity"] is not None