"""
KALATRACE Robotics Sensor Fusion Tests

Tests the Sensor Fusion engine responsible for
combining information from multiple sensors.
"""

from skills.robotics.perception.sensor_fusion import SensorFusion
from skills.robotics.perception.sensors.camera_sensor import CameraSensor
from skills.robotics.perception.sensors.thermal_sensor import ThermalSensor
from skills.robotics.perception.sensors.lidar_sensor import LidarSensor
from skills.robotics.perception.sensors.force_sensor import ForceSensor
from skills.robotics.perception.sensors.battery_sensor import BatterySensor


def create_fusion():

    fusion = SensorFusion()

    camera = CameraSensor(
        sensor_id="CAM-001",
        resolution=(1920, 1080),
        manufacturer="KALATRACE Vision"
    )

    thermal = ThermalSensor(
        sensor_id="THERM-001",
        temperature_range=(-20, 120),
        resolution=0.1,
        manufacturer="KALATRACE Thermal"
    )

    lidar = LidarSensor(
        sensor_id="LIDAR-001",
        range_limit=50,
        manufacturer="KALATRACE LiDAR"
    )

    force = ForceSensor(
        sensor_id="FORCE-001",
        force_range=(0, 100),
        resolution=0.1,
        manufacturer="KALATRACE Force"
    )

    battery = BatterySensor(
        sensor_id="BAT-001",
        battery_capacity=5000
    )

    fusion.register_sensor(camera)
    fusion.register_sensor(thermal)
    fusion.register_sensor(lidar)
    fusion.register_sensor(force)
    fusion.register_sensor(battery)

    return (
        fusion,
        camera,
        thermal,
        lidar,
        force,
        battery
    )

def activate_all(*sensors):

    for sensor in sensors:
        sensor.activate()


def test_sensor_registration():

    fusion, *_ = create_fusion()

    assert len(fusion.sensors) == 5


def test_sensor_unregistration():

    fusion, *_ = create_fusion()

    fusion.unregister_sensor("BAT-001")

    assert len(fusion.sensors) == 4

    assert "BAT-001" not in fusion.sensors


def test_update_and_collect():

    fusion, *_ = create_fusion()

    fusion.update_reading(
        "CAM-001",
        {
            "image": "frame001"
        }
    )

    readings = fusion.collect()

    assert "CAM-001" in readings

    assert readings["CAM-001"]["image"] == "frame001"


def test_fusion_process():

    (
        fusion,
        camera,
        thermal,
        lidar,
        force,
        battery
    ) = create_fusion()

    activate_all(
        camera,
        thermal,
        lidar,
        force,
        battery
    )

    fusion.update_reading(
        "CAM-001",
        {
            "objects": 2
        }
    )

    fusion.update_reading(
        "THERM-001",
        {
            "temperature": 36.7
        }
    )

    fusion.update_reading(
        "LIDAR-001",
        {
            "distance": 2.8
        }
    )

    fusion.update_reading(
        "FORCE-001",
        {
            "force": 0
        }
    )

    fusion.update_reading(
        "BAT-001",
        {
            "battery": 84
        }
    )

    result = fusion.fuse()

    assert result["sensor_count"] == 5

    assert len(result["readings"]) == 5


def test_build_observation():

    fusion, *_ = create_fusion()

    fusion.update_reading(
        "CAM-001",
        {
            "image": "frame"
        }
    )

    fusion.fuse()

    observation = fusion.build_observation()

    assert observation["type"] == "sensor_fusion"

    assert "data" in observation


def test_fusion_history():

    fusion, *_ = create_fusion()

    fusion.update_reading(
        "CAM-001",
        {
            "frame": 1
        }
    )

    fusion.fuse()

    fusion.update_reading(
        "CAM-001",
        {
            "frame": 2
        }
    )

    fusion.fuse()

    history = fusion.history()

    assert len(history) == 2


def test_get_last_fusion():

    fusion, *_ = create_fusion()

    fusion.update_reading(
        "CAM-001",
        {
            "frame": 10
        }
    )

    fusion.fuse()

    latest = fusion.get_last_fusion()

    assert latest["sensor_count"] == 1

    assert latest["readings"]["CAM-001"]["frame"] == 10


def test_clear_runtime():

    fusion, *_ = create_fusion()

    fusion.update_reading(
        "CAM-001",
        {
            "frame": 1
        }
    )

    fusion.fuse()

    fusion.clear()

    assert fusion.collect() == {}

    assert fusion.history() == []

    assert fusion.get_last_fusion() is None