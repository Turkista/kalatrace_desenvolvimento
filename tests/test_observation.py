"""
Tests for KALATRACE Robotics Observation Model
"""


from datetime import datetime

from skills.robotics.perception.observation import Observation



def test_observation_creation():

    observation = Observation(
        observation_id="OBS-001",
        robot_id="ROBOT-001",
        sensor_id="CAMERA-001",
        observation_type="object_detection",
        value="human",
        unit="class",
        confidence=0.95,
        location="laboratory",
        context={
            "environment": "indoor"
        }
    )


    assert observation.observation_id == "OBS-001"

    assert observation.robot_id == "ROBOT-001"

    assert observation.sensor_id == "CAMERA-001"

    assert observation.observation_type == "object_detection"

    assert observation.value == "human"

    assert observation.unit == "class"

    assert observation.confidence == 0.95

    assert observation.location == "laboratory"

    assert observation.context["environment"] == "indoor"



def test_observation_timestamp():

    observation = Observation(
        observation_id="OBS-002",
        robot_id="ROBOT-001",
        sensor_id="LIDAR-001",
        observation_type="distance_measurement",
        value=2.5,
        unit="meters"
    )


    assert isinstance(
        observation.created_at,
        datetime
    )


    assert observation.created_at.tzinfo is not None



def test_observation_to_dict():

    observation = Observation(
        observation_id="OBS-003",
        robot_id="ROBOT-002",
        sensor_id="THERMAL-001",
        observation_type="temperature",
        value=36.7,
        unit="celsius",
        confidence=0.98
    )


    data = observation.to_dict()


    assert data["observation_id"] == "OBS-003"

    assert data["robot_id"] == "ROBOT-002"

    assert data["sensor_id"] == "THERMAL-001"

    assert data["type"] == "temperature"

    assert data["value"] == 36.7

    assert data["unit"] == "celsius"

    assert data["confidence"] == 0.98


    assert isinstance(
        data["created_at"],
        str
    )


    assert "+" in data["created_at"]