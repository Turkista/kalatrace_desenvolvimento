"""
Tests for RoboticsContext.
"""


from skills.robotics.robotics_context import RoboticsContext



def test_create_robot_context():

    robot = RoboticsContext(
        "LAB-001"
    )


    assert robot.robot_id == "LAB-001"

    assert robot.status == "unknown"



def test_update_robot_status():

    robot = RoboticsContext(
        "LAB-001"
    )


    robot.update_status(
        "running"
    )


    assert robot.status == "running"



def test_update_sensor():

    robot = RoboticsContext(
        "LAB-001"
    )


    robot.update_sensor(
        "temperature",
        37.5
    )


    assert robot.sensors["temperature"] == 37.5