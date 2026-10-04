"""
KALATRACE Robotics Skill

Provides robotic agent integration
capabilities for the KALATRACE ecosystem.
"""

from .robotics_skill import RoboticsSkill
from .robotics_context import RoboticsContext
from .robotics_events import (
    RobotConnected,
    RobotDisconnected,
    SensorUpdated,
    MissionStarted,
    MissionCompleted,
    ObjectDetected,
    ErrorDetected
)


__version__ = "1.0.0"


__all__ = [

    "RoboticsSkill",

    "RoboticsContext",

    "RobotConnected",

    "RobotDisconnected",

    "SensorUpdated",

    "MissionStarted",

    "MissionCompleted",

    "ObjectDetected",

    "ErrorDetected"
]