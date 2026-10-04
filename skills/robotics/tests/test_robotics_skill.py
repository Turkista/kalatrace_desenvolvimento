"""
Tests for RoboticsSkill.
"""


from skills.robotics.robotics_skill import RoboticsSkill

from skills.robotics.robotics_events import (
    SensorUpdated
)



def test_robotics_skill_activation():

    skill = RoboticsSkill()


    skill.initialize()

    skill.activate()


    assert skill.active is True



def test_register_robot():

    skill = RoboticsSkill()


    robot = skill.register_robot(
        "LAB-001"
    )


    assert robot.robot_id == "LAB-001"



def test_process_sensor_event():

    skill = RoboticsSkill()


    event = SensorUpdated(
        "LAB-001",
        "temperature",
        37.5
    )


    context = skill.process_event(
        event
    )


    assert context.sensors["temperature"] == 37.5