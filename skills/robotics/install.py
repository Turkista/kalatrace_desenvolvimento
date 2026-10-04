"""
KALATRACE Robotics Skill Installer

Registers the Robotics Skill into the
KALATRACE Skill ecosystem.

This module does not execute the Skill.
It only performs the installation step
through the SkillManager.
"""


from skills.robotics.robotics_skill import RoboticsSkill



SKILL_NAME = "robotics"

SKILL_VERSION = "1.0.0"

SKILL_DESCRIPTION = (
    "Provides robotic agent integration, "
    "context management and event processing "
    "capabilities for KALATRACE."
)



def install(
    skill_manager
):
    """
    Install Robotics Skill into KALATRACE.

    Args:
        skill_manager:
            Instance of KALATRACE SkillManager.
    """


    robotics_skill = RoboticsSkill()


    skill_manager.install_skill(

        skill_name=SKILL_NAME,

        skill_instance=robotics_skill,

        version=SKILL_VERSION,

        description=SKILL_DESCRIPTION

    )


    return robotics_skill