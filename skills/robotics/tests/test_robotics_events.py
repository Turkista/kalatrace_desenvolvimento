"""
Tests for Robotics Events.
"""


from skills.robotics.robotics_events import (
    RobotConnected,
    SensorUpdated
)



def test_robot_connected_event():

    event = RobotConnected(
        "LAB-001"
    )


    assert event.robot_id == "LAB-001"

    assert event.event_type == "robot_connected"



def test_sensor_event():

    event = SensorUpdated(
        "LAB-001",
        "temperature",
        37.5
    )


    assert event.data["sensor"] == "temperature"

    assert event.data["value"] == 37.5