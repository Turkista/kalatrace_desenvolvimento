"""
KALATRACE Resource Allocator

Implements the "Resource Allocation" responsibility described
for the Command & Mission Center: missions declare which
resources they need, and the CMC coordinates who holds what,
preventing over-allocation and providing an auditable record
of every grant and release.

Mirrors the structure of core.command.CommandCenter and
core.decision.DecisionController.
"""

from __future__ import annotations

from .resource import Resource
from .resource_allocation import ResourceAllocation, AllocationStatus
from .resource_registry import ResourceRegistry


class ResourceAllocator:
    """
    Coordinates resource registration and allocation.
    """

    def __init__(self, registry: ResourceRegistry | None = None) -> None:
        """
        Initializes the resource allocator.
        """

        if registry is not None and not isinstance(registry, ResourceRegistry):
            raise TypeError(
                "registry must be a ResourceRegistry."
            )

        self.registry = registry or ResourceRegistry()

        self.allocations: dict[str, ResourceAllocation] = {}

    # =================================================
    # Internal helpers
    # =================================================

    def _get_resource(self, resource_id: str) -> Resource:

        resource = self.registry.get(resource_id)

        if resource is None:
            raise ValueError(
                f"Resource not found: {resource_id}"
            )

        return resource

    def _get_allocation(self, allocation_id: str) -> ResourceAllocation:

        allocation = self.allocations.get(allocation_id)

        if allocation is None:
            raise ValueError(
                f"Allocation not found: {allocation_id}"
            )

        return allocation

    # =================================================
    # Resource registration
    # =================================================

    def register_resource(
        self,
        name: str,
        total_capacity: float,
        unit: str = "units",
        resource_type: str = "GENERIC",
    ) -> Resource:
        """
        Registers a new allocatable resource.
        """

        resource = Resource(
            name=name,
            total_capacity=total_capacity,
            unit=unit,
            resource_type=resource_type,
        )

        self.registry.register(resource)

        return resource

    # =================================================
    # Allocation
    # =================================================

    def allocate(
        self,
        resource_id: str,
        amount: float,
        mission_id: str | None = None,
    ) -> ResourceAllocation:
        """
        Allocates a portion of a resource's capacity to a
        mission, if enough capacity is available.
        """

        resource = self._get_resource(resource_id)

        resource.reserve(amount)

        allocation = ResourceAllocation(
            resource_id=resource_id,
            amount=amount,
            mission_id=mission_id,
        )

        self.allocations[allocation.allocation_id] = allocation

        return allocation

    def release(self, allocation_id: str) -> ResourceAllocation:
        """
        Releases a previously granted allocation, freeing
        capacity back onto the resource.
        """

        allocation = self._get_allocation(allocation_id)

        if allocation.status == AllocationStatus.RELEASED:
            return allocation

        resource = self._get_resource(allocation.resource_id)

        resource.free(allocation.amount)

        allocation.mark_released()

        return allocation

    # =================================================
    # Queries
    # =================================================

    def get_resource(self, resource_id: str) -> Resource | None:

        return self.registry.get(resource_id)

    def list_resources(self) -> list[Resource]:

        return self.registry.list_all()

    def available_capacity(self, resource_id: str) -> float:

        return self._get_resource(resource_id).available_capacity

    def get_allocation(self, allocation_id: str) -> ResourceAllocation | None:

        return self.allocations.get(allocation_id)

    def list_allocations(self) -> list[ResourceAllocation]:

        return list(self.allocations.values())

    def list_allocations_by_mission(
        self,
        mission_id: str,
    ) -> list[ResourceAllocation]:

        return [
            allocation
            for allocation in self.allocations.values()
            if allocation.mission_id == mission_id
        ]

    # =================================================
    # Observability
    # =================================================

    def stats(self) -> dict:
        """
        Returns Resource Allocator status.
        """

        registry_stats = self.registry.stats()

        active_allocations = [
            allocation
            for allocation in self.allocations.values()
            if allocation.status == AllocationStatus.ALLOCATED
        ]

        return {

            **registry_stats,

            "total_allocations": len(self.allocations),

            "active_allocations": len(active_allocations),

        }

    def __repr__(self) -> str:

        return (
            f"<ResourceAllocator "
            f"resources={self.registry.count()} "
            f"allocations={len(self.allocations)}>"
        )
