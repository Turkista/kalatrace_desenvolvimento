"""
KALATRACE Robotics Connector Tests

Validates the communication layer
between a robotic agent and KALATRACE.
"""


from skills.skill_manager import SkillManager

from skills.robotics.install import install

from skills.robotics.robotics_api import RoboticsAPI

from skills.robotics.robotics_connector import RoboticsConnector



def create_robot():

    manager = SkillManager()


    robotics_skill = install(
        manager
    )


    manager.initialize_skill(
        "robotics"
    )


    manager.activate_skill(
        "robotics"
    )


    api = RoboticsAPI(
        robotics_skill
    )


    robot = RoboticsConnector(
        "LAB-001",
        api
    )


    return robot



def test_robot_connection():

    robot = create_robot()


    result = robot.connect(
        {
            "model": "Research Robot"
        }
    )


    assert result["robot_id"] == "LAB-001"

    assert result["status"] == "connected"



def test_robot_send_sensor_data():

    robot = create_robot()


    robot.connect()


    result = robot.send_sensor_data(
        "temperature",
        36.8
    )


    assert (
        result["sensors"]["temperature"]
        == 36.8
    )



def test_robot_execute_task():

    robot = create_robot()


    robot.connect()


    result = robot.start_task(
        "Material Inspection"
    )


    assert (
        result["mission"]
        == "Material Inspection"
    )

    assert (
        result["status"]
        == "executing"
    )



def test_robot_state_query():

    robot = create_robot()


    robot.connect()


    robot.send_sensor_data(
        "battery",
        95
    )


    state = robot.get_state()


    assert state["robot_id"] == "LAB-001"


    assert (
        state["sensors"]["battery"]
        == 95
    )