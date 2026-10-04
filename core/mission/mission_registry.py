"""
KALATRACE Mission Registry

Maintains the registry of missions managed
by the Command & Mission Center.

Responsibilities:

- register missions
- retrieve missions
- remove missions
- list active missions
"""


from typing import Dict, List


from .mission import Mission
from .mission_state import MissionState



class MissionRegistry:
    """
    Central registry for KALATRACE missions.
    """



    def __init__(
        self,
    ):
        """
        Initializes the mission storage.
        """


        self._missions: Dict[
            str,
            Mission
        ] = {}



    # =================================================
    # Registration
    # =================================================


    def register(
        self,
        mission: Mission,
    ) -> None:
        """
        Registers a mission.
        """


        if not isinstance(
            mission,
            Mission,
        ):
            raise TypeError(
                "Registry requires a Mission instance."
            )


        if mission.mission_id in self._missions:
            raise ValueError(
                f"Mission already registered: "
                f"{mission.mission_id}"
            )


        self._missions[
            mission.mission_id
        ] = mission



    def unregister(
        self,
        mission_id: str,
    ) -> None:
        """
        Removes a mission from registry.
        """


        if mission_id not in self._missions:
            raise KeyError(
                f"Mission not found: {mission_id}"
            )


        del self._missions[
            mission_id
        ]



    # =================================================
    # Query
    # =================================================


    def get(
        self,
        mission_id: str,
    ) -> Mission | None:
        """
        Retrieves a mission by identifier.
        """


        return self._missions.get(
            mission_id
        )



    def exists(
        self,
        mission_id: str,
    ) -> bool:
        """
        Checks if a mission exists.
        """


        return mission_id in self._missions



    def list_all(
        self,
    ) -> List[Mission]:
        """
        Returns all registered missions.
        """


        return list(
            self._missions.values()
        )



    def list_active(
        self,
    ) -> List[Mission]:
        """
        Returns missions currently active.
        """


        active_states = {

            MissionState.PLANNING,

            MissionState.READY,

            MissionState.EXECUTING,

            MissionState.PAUSED,

            MissionState.WAITING_ANALYSIS,

            MissionState.VALIDATING,

        }



        return [

            mission

            for mission
            in self._missions.values()

            if mission.status
            in active_states

        ]



    def count(
        self,
    ) -> int:
        """
        Returns total number of missions.
        """


        return len(
            self._missions
        )



    def clear(
        self,
    ) -> None:
        """
        Removes all missions from registry.
        """

        self._missions.clear()