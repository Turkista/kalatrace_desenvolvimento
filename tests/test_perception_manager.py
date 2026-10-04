"""
KALATRACE Robotics Perception Manager Tests

Tests the PerceptionManager responsible for
sensor registration and observation generation.
"""

import pytest

from skills.robotics.perception.perception_manager import PerceptionManager
from skills.robotics.perception.sensors.camera_sensor import CameraSensor
from skills.robotics.perception.sensors.thermal_sensor import ThermalSensor


@pytest.fixture
def manager():

    return PerceptionManager(
        robot_id="ROBOT-001"
    )


@pytest.fixture
def camera():

    return CameraSensor(
        sensor_id="CAM-001",
        resolution=(1920, 1080),
        manufacturer="KALATRACE Vision"
    )


@pytest.fixture
def thermal():

    return ThermalSensor(
        sensor_id="THERM-001",
        temperature_range=(-20, 120),
        resolution=0.1,
        manufacturer="KALATRACE Thermal"
    )


def test_manager_initialization(manager):

    assert manager.robot_id == "ROBOT-001"

    assert manager.sensor_count() == 0

    assert manager.get_observations() == []


def test_register_sensor(manager, camera):

    manager.register_sensor(camera)

    assert manager.sensor_count() == 1

    assert manager.has_sensor("CAM-001")


def test_unregister_sensor(manager, camera):

    manager.register_sensor(camera)

    manager.unregister_sensor("CAM-001")

    assert manager.sensor_count() == 0

    assert not manager.has_sensor("CAM-001")


def test_register_multiple_sensors(
    manager,
    camera,
    thermal
):

    manager.register_sensor(camera)

    manager.register_sensor(thermal)

    assert manager.sensor_count() == 2


def test_collect_camera_observation(
    manager,
    camera
):

    manager.register_sensor(camera)

    manager.activate_sensor("CAM-001")

    observation = manager.collect_data(

        sensor_id="CAM-001",

        value="frame_001.jpg",

        confidence=0.98,

        location="Front Camera"
    )

    assert observation.robot_id == "ROBOT-001"

    assert observation.sensor_id == "CAM-001"

    assert observation.value == "frame_001.jpg"


def test_collect_thermal_observation(
    manager,
    thermal
):

    manager.register_sensor(thermal)

    manager.activate_sensor("THERM-001")

    observation = manager.collect_data(

        sensor_id="THERM-001",

        value=36.8,

        confidence=0.95
    )

    assert observation.sensor_id == "THERM-001"

    assert observation.value == 36.8


def test_clear_observations(
    manager,
    camera
):

    manager.register_sensor(camera)

    manager.activate_sensor("CAM-001")

    manager.collect_data(

        sensor_id="CAM-001",

        value="frame.jpg"
    )

    assert len(manager.get_observations()) == 1

    manager.clear()

    assert manager.get_observations() == []


def test_export(manager, camera):

    manager.register_sensor(camera)

    exported = manager.export()

    assert exported["robot_id"] == "ROBOT-001"

    assert exported["sensor_count"] == 1

    assert exported["observation_count"] == 0

    assert exported["sensors"] == ["CAM-001"]

    assert "observations" in exported