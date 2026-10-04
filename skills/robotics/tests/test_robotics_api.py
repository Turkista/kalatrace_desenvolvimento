"""
Tests for Robotics API.
"""


from skills.robotics.robotics_skill import RoboticsSkill

from skills.robotics.robotics_api import RoboticsAPI



def test_robotics_api_connection():

    skill = RoboticsSkill()


    api = RoboticsAPI(
        skill
    )


    result = api.connect_robot(
        "LAB-001"
    )


    assert result["robot_id"] == "LAB-001"

    assert result["status"] == "connected"



def test_sensor_update_api():

    skill = RoboticsSkill()


    api = RoboticsAPI(
        skill
    )


    api.connect_robot(
        "LAB-001"
    )


    result = api.update_sensor(
        "LAB-001",
        "temperature",
        37.5
    )


    assert (
        result["sensors"]["temperature"]
        == 37.5
    )