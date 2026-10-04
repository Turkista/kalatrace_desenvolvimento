"""
KALATRACE Robotics Skill Integration Test

Validates the complete lifecycle of the
Robotics Skill inside the KALATRACE ecosystem.

Test flow:

SkillManager
    ↓
Install Robotics Skill
    ↓
SkillRegistry
    ↓
Initialize
    ↓
Activate
    ↓
Process Robot Event
    ↓
Update Robot Context
"""


from skills.skill_manager import SkillManager

from skills.robotics.install import install

from skills.robotics.robotics_events import (
    RobotConnected,
    SensorUpdated
)



def test_robotics_skill_installation():

    manager = SkillManager()


    robotics_skill = install(
        manager
    )


    assert manager.registry.exists(
        "robotics"
    )


    assert "robotics" in manager.loaded_skills


    assert robotics_skill is not None



def test_robotics_skill_lifecycle():

    manager = SkillManager()


    install(
        manager
    )


    manager.initialize_skill(
        "robotics"
    )


    status = manager.get_skill_status(
        "robotics"
    )


    assert status["status"] == "initialized"



    manager.activate_skill(
        "robotics"
    )


    status = manager.get_skill_status(
        "robotics"
    )


    assert status["status"] == "active"



def test_robot_event_processing():

    manager = SkillManager()


    robotics = install(
        manager
    )


    manager.initialize_skill(
        "robotics"
    )


    manager.activate_skill(
        "robotics"
    )


    event = RobotConnected(
        "LAB-001"
    )


    manager.process_event(
        "robotics",
        event
    )


    context = robotics.get_robot_context(
        "LAB-001"
    )


    assert context is not None


    assert context.status == "connected"



def test_robot_sensor_update():

    manager = SkillManager()


    robotics = install(
        manager
    )


    manager.initialize_skill(
        "robotics"
    )


    manager.activate_skill(
        "robotics"
    )


    event = SensorUpdated(
        "LAB-001",
        "temperature",
        37.5
    )


    manager.process_event(
        "robotics",
        event
    )


    context = robotics.get_robot_context(
        "LAB-001"
    )


    assert context.sensors["temperature"] == 37.5