"""
KALATRACE Skill Framework Test

Validates the complete lifecycle of a Skill:

- Installation
- Registration
- Initialization
- Activation
- Event processing
- Deactivation
"""

from skills.skill_manager import SkillManager
from examples.skills.example_skill import ExampleSkill


def test_skill_lifecycle():

    # Create Skill Manager
    manager = SkillManager()

    # Create Example Skill
    example_skill = ExampleSkill()

    # Install Skill
    manager.install_skill(
        skill_name="example",
        skill_instance=example_skill,
        version="1.0",
        description="KALATRACE example test skill"
    )

    # Check registration
    skill_info = manager.get_skill_status(
        "example"
    )

    assert skill_info["name"] == "example"
    assert skill_info["status"] == "registered"


    # Initialize Skill
    manager.initialize_skill(
        "example"
    )

    skill_info = manager.get_skill_status(
        "example"
    )

    assert skill_info["status"] == "initialized"


    # Activate Skill
    manager.activate_skill(
        "example"
    )

    skill_info = manager.get_skill_status(
        "example"
    )

    assert skill_info["status"] == "active"


    # Send event
    manager.process_event(
        "example",
        {
            "type": "test_event",
            "message": "KALATRACE Skill Framework working"
        }
    )

    assert example_skill.events_received == 1


    # Deactivate Skill
    manager.deactivate_skill(
        "example"
    )

    skill_info = manager.get_skill_status(
        "example"
    )

    assert skill_info["status"] == "inactive"