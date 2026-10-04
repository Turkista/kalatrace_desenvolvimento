"""
KALATRACE Resource Entity

Represents an allocatable resource managed by the
Command & Mission Center's Resource Allocation layer.

A resource has a finite capacity (e.g. compute hours, agent
slots, budget units) that missions can request and later
release. The entity itself only tracks capacity accounting;
allocation bookkeeping (which mission holds how much, and
since when) belongs to ResourceAllocation records managed by
the ResourceAllocator facade.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4


class Resource:
    """
    Represents an allocatable resource.
    """

    def __init__(
        self,
        name: str,
        total_capacity: float,
        unit: str = "units",
        resource_type: str = "GENERIC",
        resource_id: str | None = None,
    ) -> None:
        """
        Creates a resource.
        """

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                "Resource name cannot be empty."
            )

        if not isinstance(total_capacity, (int, float)) or isinstance(total_capacity, bool):
            raise TypeError(
                "total_capacity must be a number."
            )

        if total_capacity < 0:
            raise ValueError(
                "total_capacity cannot be negative."
            )

        if not isinstance(unit, str) or not unit.strip():
            raise ValueError(
                "unit cannot be empty."
            )

        if not isinstance(resource_type, str) or not resource_type.strip():
            raise ValueError(
                "resource_type cannot be empty."
            )

        self.resource_id = (
            resource_id.strip()
            if resource_id
            else str(uuid4())
        )

        self.name = name.strip()

        self.total_capacity = float(total_capacity)

        self.unit = unit.strip()

        self.resource_type = resource_type.strip().upper()

        self._allocated: float = 0.0

        now = datetime.now(UTC)

        self.created_at = now

        self.updated_at = now

    # =================================================
    # Capacity accounting
    # =================================================

    @property
    def allocated(self) -> float:
        """
        Currently allocated capacity.
        """

        return self._allocated

    @property
    def available_capacity(self) -> float:
        """
        Remaining capacity available for allocation.
        """

        return self.total_capacity - self._allocated

    def can_allocate(self, amount: float) -> bool:
        """
        Checks whether the requested amount fits within
        remaining capacity.
        """

        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError(
                "amount must be a number."
            )

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        return amount <= self.available_capacity

    def reserve(self, amount: float) -> None:
        """
        Reserves capacity for an allocation.

        Called by ResourceAllocator only, after
        can_allocate() has been verified.
        """

        if not self.can_allocate(amount):
            raise ValueError(
                f"Insufficient capacity on resource "
                f"'{self.name}': requested {amount}, "
                f"available {self.available_capacity}."
            )

        self._allocated += float(amount)

        self.updated_at = datetime.now(UTC)

    def free(self, amount: float) -> None:
        """
        Releases previously reserved capacity.
        """

        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError(
                "amount must be a number."
            )

        if amount <= 0:
            raise ValueError(
                "amount must be greater than zero."
            )

        self._allocated = max(0.0, self._allocated - float(amount))

        self.updated_at = datetime.now(UTC)

    # =================================================
    # Serialization
    # =================================================

    def to_dict(self) -> dict[str, Any]:

        return {

            "resource_id": self.resource_id,

            "name": self.name,

            "resource_type": self.resource_type,

            "total_capacity": self.total_capacity,

            "allocated": self.allocated,

            "available_capacity": self.available_capacity,

            "unit": self.unit,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

        }

    def __repr__(self) -> str:

        return (
            f"<Resource "
            f"id={self.resource_id} "
            f"name={self.name!r} "
            f"available={self.available_capacity}/{self.total_capacity} "
            f"{self.unit}>"
        )
