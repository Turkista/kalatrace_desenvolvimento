"""
KALATRACE Core

Mission Contract

Defines the abstraction for missions executed
within the KALATRACE architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class MissionStatus(Enum):
    """
    Mission execution states.
    """

    CREATED = "created"

    PLANNING = "planning"

    PLANNED = "planned"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class MissionContract(ABC):
    """
    Base contract for KALATRACE missions.

    Missions represent goal-oriented execution flows.
    """


    def __init__(self) -> None:

        self._status = (
            MissionStatus.CREATED
        )

        self._result: Any = None


    @property
    @abstractmethod
    def mission_id(self) -> str:
        """
        Returns the mission identifier.
        """
        ...


    @property
    @abstractmethod
    def objective(self) -> str:
        """
        Returns the mission objective.
        """
        ...


    @property
    def status(self) -> MissionStatus:
        """
        Returns current mission status.
        """

        return self._status


    def update_status(
        self,
        status: MissionStatus,
    ) -> None:
        """
        Updates mission status.
        """

        self._status = status


    @abstractmethod
    def plan(self) -> list[Any]:
        """
        Generates execution plan.
        """
        ...


    @abstractmethod
    def validate(self) -> bool:
        """
        Validates mission requirements.
        """
        ...


    @property
    def result(self) -> Any:
        """
        Returns mission result.
        """

        return self._result


    def set_result(
        self,
        result: Any,
    ) -> None:
        """
        Stores mission result.
        """

        self._result = result