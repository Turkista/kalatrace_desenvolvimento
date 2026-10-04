"""
KALATRACE Mission State Management

Defines mission lifecycle states and
validated state transitions.

The state machine guarantees that missions
follow controlled lifecycle evolution.
"""


from enum import Enum



class MissionState(str, Enum):
    """
    Possible states of a mission lifecycle.
    """


    CREATED = "CREATED"

    PLANNING = "PLANNING"

    READY = "READY"

    EXECUTING = "EXECUTING"

    PAUSED = "PAUSED"

    WAITING_ANALYSIS = "WAITING_ANALYSIS"

    VALIDATING = "VALIDATING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    ARCHIVED = "ARCHIVED"



    def is_final(
        self,
    ) -> bool:
        """
        Checks whether state is terminal.
        """

        return self in {

            MissionState.ARCHIVED,

        }



    def is_active(
        self,
    ) -> bool:
        """
        Checks whether mission is active.
        """

        return self in {

            MissionState.PLANNING,

            MissionState.READY,

            MissionState.EXECUTING,

            MissionState.PAUSED,

            MissionState.WAITING_ANALYSIS,

            MissionState.VALIDATING,

        }





class MissionStateMachine:
    """
    Controls mission lifecycle transitions.

    Prevents invalid state changes.
    """


    VALID_TRANSITIONS = {


        MissionState.CREATED: (

            MissionState.PLANNING,

        ),



        MissionState.PLANNING: (

            MissionState.READY,

            MissionState.FAILED,

        ),



        MissionState.READY: (

            MissionState.EXECUTING,

        ),



        MissionState.EXECUTING: (

            MissionState.PAUSED,

            MissionState.WAITING_ANALYSIS,

            MissionState.FAILED,

        ),



        MissionState.PAUSED: (

            MissionState.EXECUTING,

            MissionState.FAILED,

        ),



        MissionState.WAITING_ANALYSIS: (

            MissionState.VALIDATING,

            MissionState.EXECUTING,

            MissionState.FAILED,

        ),



        MissionState.VALIDATING: (

            MissionState.COMPLETED,

            MissionState.FAILED,

        ),



        MissionState.COMPLETED: (

            MissionState.ARCHIVED,

        ),



        MissionState.FAILED: (

            MissionState.ARCHIVED,

        ),



        MissionState.ARCHIVED: ()

    }



    @classmethod
    def can_transition(
        cls,
        current_state: MissionState,
        next_state: MissionState,
    ) -> bool:
        """
        Checks whether transition is allowed.
        """


        if not isinstance(
            current_state,
            MissionState,
        ):
            return False


        if not isinstance(
            next_state,
            MissionState,
        ):
            return False



        return next_state in cls.VALID_TRANSITIONS.get(
            current_state,
            (),
        )



    @classmethod
    def transition(
        cls,
        current_state: MissionState,
        next_state: MissionState,
    ) -> MissionState:
        """
        Performs validated transition.
        """


        if not isinstance(
            current_state,
            MissionState,
        ):
            raise TypeError(
                "current_state must be MissionState."
            )


        if not isinstance(
            next_state,
            MissionState,
        ):
            raise TypeError(
                "next_state must be MissionState."
            )



        if not cls.can_transition(
            current_state,
            next_state,
        ):
            raise ValueError(
                f"Invalid mission transition: "
                f"{current_state.value} -> "
                f"{next_state.value}"
            )



        return next_state



    @classmethod
    def is_final_state(
        cls,
        state: MissionState,
    ) -> bool:
        """
        Checks whether state is terminal.
        """

        if not isinstance(
            state,
            MissionState,
        ):
            return False


        return state.is_final()



    @classmethod
    def is_active_state(
        cls,
        state: MissionState,
    ) -> bool:
        """
        Checks whether state represents
        an active mission.
        """

        if not isinstance(
            state,
            MissionState,
        ):
            return False


        return state.is_active()