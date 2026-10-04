"""
KALATRACE Mission Module

Provides mission lifecycle management
for the Command & Mission Center.

The mission layer is responsible for:

- Mission definition
- Mission lifecycle control
- Mission state transitions
- Mission registry management
- Mission timeline tracking

Public API:

- Mission
- MissionState
- MissionStateMachine
- MissionRegistry
- MissionManager
- MissionTimeline
- MissionEvent
"""


from __future__ import annotations



from .mission import Mission


from .mission_state import (
    MissionState,
    MissionStateMachine,
)


from .mission_registry import (
    MissionRegistry,
)


from .mission_manager import (
    MissionManager,
)


from .mission_timeline import (
    MissionTimeline,
    MissionEvent,
)



__all__ = [

    "Mission",

    "MissionState",

    "MissionStateMachine",

    "MissionRegistry",

    "MissionManager",

    "MissionTimeline",

    "MissionEvent",

]