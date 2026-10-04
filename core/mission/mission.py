"""
KALATRACE Mission Entity

Defines the core representation of a mission.

A mission represents an intentional objective
managed by the Command & Mission Center.
"""


from datetime import datetime, UTC
from uuid import uuid4


from .mission_state import (
    MissionState,
    MissionStateMachine,
)



class Mission:
    """
    Represents a KALATRACE mission.

    A mission is the highest-level operational
    unit controlled by the Command & Mission Center.
    """


    def __init__(
        self,
        name: str,
        objective: str,
        priority: str = "NORMAL",
        mission_id: str | None = None,
        project_id: str | None = None,
    ):
        """
        Initialize a mission.
        """


        if not name or not name.strip():
            raise ValueError(
                "Mission name cannot be empty."
            )


        if not objective or not objective.strip():
            raise ValueError(
                "Mission objective cannot be empty."
            )


        self.mission_id = (
            mission_id.strip()
            if mission_id
            else str(uuid4())
        )


        self.name = name.strip()

        self.objective = objective.strip()

        self.priority = priority.upper()
        self.project_id = project_id


        self.status = MissionState.CREATED


        now = datetime.now(UTC)

        self.created_at = now

        self.updated_at = now


        self.commands = []

        self.decisions = []

        self.resources = []

        self.timeline = []


        self.add_timeline_event(
            "Mission created"
        )



    # =================================================
    # Lifecycle
    # =================================================


    def change_state(
        self,
        next_state: MissionState,
    ) -> None:
        """
        Changes mission lifecycle state.
        """


        if not isinstance(
            next_state,
            MissionState,
        ):
            raise TypeError(
                "next_state must be MissionState."
            )


        new_state = (
            MissionStateMachine.transition(
                self.status,
                next_state,
            )
        )


        self.status = new_state


        self.add_timeline_event(
            f"Mission state changed to {new_state.value}"
        )


        self._update_timestamp()



    def start(self):

        self.change_state(
            MissionState.EXECUTING
        )



    def complete(self):

        self.change_state(
            MissionState.COMPLETED
        )



    def fail(
        self,
        reason: str,
    ):

        self.change_state(
            MissionState.FAILED
        )


        self.add_timeline_event(
            f"Failure reason: {reason}"
        )



    # =================================================
    # Tracking
    # =================================================


    def add_command(
        self,
        command,
    ):

        self.commands.append(
            command
        )


        self.add_timeline_event(
            "Command added"
        )


        self._update_timestamp()



    def add_decision(
        self,
        decision,
    ):

        self.decisions.append(
            decision
        )


        self.add_timeline_event(
            "Decision registered"
        )


        self._update_timestamp()



    def add_resource_allocation(
        self,
        allocation,
    ):

        self.resources.append(
            allocation
        )


        self.add_timeline_event(
            "Resource allocated"
        )


        self._update_timestamp()



    def add_timeline_event(
        self,
        event: str,
    ):

        self.timeline.append(
            {
                "timestamp":
                    datetime.now(UTC),

                "event":
                    event,
            }
        )



    # =================================================
    # Information
    # =================================================


    def summary(
        self,
    ) -> dict:

        return {

            "mission_id":
                self.mission_id,

            "name":
                self.name,

            "objective":
                self.objective,

            "priority":
                self.priority,

            "project_id":
                self.project_id,

            "status":
                self.status.value,

            "commands":
                len(self.commands),

            "decisions":
                len(self.decisions),

            "resources":
                len(self.resources),

            "timeline_events":
                len(self.timeline),

        }



    # =================================================
    # Internal
    # =================================================


    def _update_timestamp(
        self,
    ) -> None:

        self.updated_at = datetime.now(UTC)



    def __repr__(
        self,
    ) -> str:

        return (
            f"<Mission "
            f"id={self.mission_id} "
            f"name={self.name} "
            f"status={self.status.value}>"
        )