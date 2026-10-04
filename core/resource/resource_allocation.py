"""
KALATRACE Resource Allocation

Represents a single grant of resource capacity to a mission,
issued by the Resource Allocator.
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import uuid4


class AllocationStatus(str, Enum):
    """
    Lifecycle of a resource allocation.
    """

    ALLOCATED = "ALLOCATED"

    RELEASED = "RELEASED"


class ResourceAllocation:
    """
    Represents a resource grant issued to a mission.
    """

    def __init__(
        self,
        resource_id: str,
        amount: float,
        mission_id: str | None = None,
        allocation_id: str | None = None,
    ) -> None:
        """
        Creates an allocation record.

        Note: this constructor does not touch the Resource's
        capacity accounting -- that is the ResourceAllocator's
        responsibility, so a single reservation step stays in
        one place.
        """

        if not isinstance(resource_id, str) or not resource_id.strip():
            raise ValueError(
                "resource_id cannot be empty."
            )

        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError(
                "amount must be a number."
            )

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        if mission_id is not None and not isinstance(mission_id, str):
            raise TypeError(
                "mission_id must be a string or None."
            )

        self.allocation_id = (
            allocation_id.strip()
            if allocation_id
            else str(uuid4())
        )

        self.resource_id = resource_id.strip()

        self.amount = float(amount)

        self.mission_id = mission_id

        self.status = AllocationStatus.ALLOCATED

        now = datetime.now(UTC)

        self.created_at = now

        self.released_at: datetime | None = None

    def mark_released(self) -> None:
        """
        Marks the allocation as released.
        """

        self.status = AllocationStatus.RELEASED

        self.released_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:

        return {

            "allocation_id": self.allocation_id,

            "resource_id": self.resource_id,

            "mission_id": self.mission_id,

            "amount": self.amount,

            "status": self.status.value,

            "created_at": self.created_at,

            "released_at": self.released_at,

        }

    def __repr__(self) -> str:

        return (
            f"<ResourceAllocation "
            f"id={self.allocation_id} "
            f"resource={self.resource_id} "
            f"amount={self.amount} "
            f"status={self.status.value}>"
        )
