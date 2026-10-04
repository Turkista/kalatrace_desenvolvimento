"""
KALATRACE Mission Manager

Controls mission lifecycle operations.

The MissionManager coordinates mission
operations but does not own mission state logic.

Mission state validation is delegated to:

Mission
    |
    v
MissionStateMachine
"""

from __future__ import annotations


from .mission import Mission

from .mission_state import (
    MissionState,
)

from .mission_registry import (
    MissionRegistry,
)



class MissionManager:
    """
    Coordinates mission lifecycle.
    """


    def __init__(
        self,
        registry: MissionRegistry,
    ) -> None:
        """
        Initialize mission manager.
        """

        self.registry = registry



    # =================================================
    # Creation
    # =================================================


    def create_mission(
        self,
        name: str,
        objective: str,
        priority: str = "NORMAL",
        project_id: str | None = None,
    ) -> Mission:
        """
        Creates and registers a mission.
        """


        mission = Mission(
            name=name,
            objective=objective,
            priority=priority,
            project_id=project_id,
        )


        self.registry.register(
            mission
        )


        return mission



    # =================================================
    # Lifecycle Control
    # =================================================


    def _change_state(
        self,
        mission: Mission,
        next_state: MissionState,
    ) -> Mission:
        """
        Performs mission lifecycle transition.

        State validation remains inside
        Mission entity.
        """


        mission.change_state(
            next_state
        )


        return mission



    # =================================================
    # Preparation
    # =================================================


    def prepare_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Prepares mission.

        CREATED
            |
            v
        PLANNING
            |
            v
        READY
        """


        mission = self._get_mission(
            mission_id
        )


        self._change_state(
            mission,
            MissionState.PLANNING,
        )


        self._change_state(
            mission,
            MissionState.READY,
        )


        return mission



    # =================================================
    # Execution
    # =================================================


    def start_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Starts mission execution.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.EXECUTING,
        )



    def pause_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Pauses mission execution.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.PAUSED,
        )



    def resume_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Resumes mission execution.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.EXECUTING,
        )



    # =================================================
    # Analysis
    # =================================================


    def wait_analysis(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Moves mission to analysis waiting state.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.WAITING_ANALYSIS,
        )



    def validate_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Starts mission validation.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.VALIDATING,
        )



    # =================================================
    # Completion
    # =================================================


    def complete_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Completes mission.
        """


        return self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.COMPLETED,
        )



    def fail_mission(
        self,
        mission_id: str,
        reason: str,
    ) -> Mission:
        """
        Marks mission as failed.
        """


        mission = self._change_state(
            self._get_mission(
                mission_id
            ),
            MissionState.FAILED,
        )


        mission.add_timeline_event(
            f"Failure reason: {reason}"
        )


        return mission



    # =================================================
    # Query
    # =================================================


    def get_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Returns mission.
        """

        return self._get_mission(
            mission_id
        )



    def list_active(
        self,
    ):
        """
        Returns active missions.
        """

        return self.registry.list_active()



    # =================================================
    # Internal
    # =================================================


    def _get_mission(
        self,
        mission_id: str,
    ) -> Mission:
        """
        Retrieves mission.
        """


        mission = self.registry.get(
            mission_id
        )


        if mission is None:
            raise ValueError(
                f"Mission not found: {mission_id}"
            )


        return mission