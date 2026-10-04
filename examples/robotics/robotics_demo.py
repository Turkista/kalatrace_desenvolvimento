"""
KALATRACE Robotics Demo

Simulation of a robotic agent connected
to the KALATRACE ecosystem.
"""


import sys

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from skills.skill_manager import SkillManager

from skills.robotics.install import install

from skills.robotics.robotics_api import RoboticsAPI



def main():

    print("\n=== KALATRACE Robotics Demo ===\n")


    # Create KALATRACE Skill Manager

    manager = SkillManager()


    print("Initializing Skill Manager...")


    # Install Robotics Skill

    robotics_skill = install(
        manager
    )


    print("Robotics Skill installed.")


    # Initialize Skill

    manager.initialize_skill(
        "robotics"
    )


    print("Robotics Skill initialized.")


    # Activate Skill

    manager.activate_skill(
        "robotics"
    )


    print("Robotics Skill active.\n")


    # Create external API interface

    api = RoboticsAPI(
        robotics_skill
    )


    # Connect robot

    print("Connecting robot LAB-001...")


    api.connect_robot(
        "LAB-001",
        {
            "model": "Research Robot",
            "location": "Laboratory A"
        }
    )


    # Send sensor data

    print("Sending sensor data...")


    api.update_sensor(
        "LAB-001",
        "temperature",
        37.5
    )


    api.update_sensor(
        "LAB-001",
        "battery",
        82
    )


    # Start mission

    print("Starting mission...")


    api.start_mission(
        "LAB-001",
        "Sample Analysis"
    )


    # Retrieve final state

    robot_state = api.get_robot(
        "LAB-001"
    )


    print("\n=== Robot Current State ===")

    print(robot_state)


    print("\n=== Demo Completed ===")



if __name__ == "__main__":

    main()