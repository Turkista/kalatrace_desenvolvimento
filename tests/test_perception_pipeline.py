"""
KALATRACE Robotics Perception Pipeline Tests

Tests the orchestration of the complete robotic
perception pipeline.
"""

import pytest

from skills.robotics.perception.perception_pipeline import PerceptionPipeline
from skills.robotics.perception.perception_manager import PerceptionManager
from skills.robotics.perception.sensor_fusion import SensorFusion
from skills.robotics.perception.object_tracker import ObjectTracker
from skills.robotics.perception.environment_model import EnvironmentModel


@pytest.fixture
def perception_pipeline():
    """
    Creates a complete perception pipeline.
    """

    manager = PerceptionManager(
        robot_id="ROBOT-001"
    )

    fusion = SensorFusion()

    tracker = ObjectTracker()

    environment = EnvironmentModel()

    return PerceptionPipeline(
        perception_manager=manager,
        sensor_fusion=fusion,
        object_tracker=tracker,
        environment_model=environment
    )


def test_pipeline_initialization(perception_pipeline):

    assert perception_pipeline is not None

    assert perception_pipeline.perception_manager is not None

    assert perception_pipeline.sensor_fusion is not None

    assert perception_pipeline.object_tracker is not None

    assert perception_pipeline.environment_model is not None


def test_pipeline_process_empty_runtime(perception_pipeline):

    state = perception_pipeline.process()

    assert isinstance(state, dict)

    assert "observations" in state

    assert "fusion" in state

    assert "environment" in state

    assert "tracked_objects" in state

    assert state["fusion"]["sensor_count"] == 0


def test_environment_export(perception_pipeline):

    environment = perception_pipeline.get_environment()

    assert isinstance(environment, dict)

    assert "robot_state" in environment

    assert "objects" in environment

    assert "environment" in environment


def test_object_export(perception_pipeline):

    objects = perception_pipeline.get_objects()

    assert isinstance(objects, dict)

    assert len(objects) == 0


def test_pipeline_clear(perception_pipeline):

    perception_pipeline.environment_model.add_object(
        "BOX-001",
        {
            "type": "box"
        }
    )

    perception_pipeline.object_tracker.register_object(
        "BOX-001",
        {
            "type": "box"
        }
    )

    perception_pipeline.clear()

    assert (
        perception_pipeline.environment_model.object_count()
        == 0
    )

    assert (
        perception_pipeline.object_tracker.object_count()
        == 0
    )


def test_pipeline_export(perception_pipeline):

    exported = perception_pipeline.export()

    assert isinstance(exported, dict)

    assert "observations" in exported

    assert "fusion" in exported

    assert "environment" in exported

    assert "tracked_objects" in exported