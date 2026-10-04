"""
KALATRACE Resource Allocator Tests

Validates resource registration, capacity accounting,
allocation, and release.
"""

import pytest

from core.resource import (
    Resource,
    ResourceAllocation,
    AllocationStatus,
    ResourceRegistry,
    ResourceAllocator,
)


# =====================================================
# Resource entity
# =====================================================


def test_create_resource():

    resource = Resource(
        name="Research Agent Pool",
        total_capacity=10,
        unit="agents",
        resource_type="agent",
    )

    assert resource.total_capacity == 10
    assert resource.available_capacity == 10
    assert resource.resource_type == "AGENT"


def test_resource_reserve_and_free():

    resource = Resource(name="Compute", total_capacity=100, unit="hours")

    resource.reserve(40)

    assert resource.allocated == 40
    assert resource.available_capacity == 60

    resource.free(15)

    assert resource.allocated == 25
    assert resource.available_capacity == 75


def test_resource_reserve_beyond_capacity_fails():

    resource = Resource(name="Compute", total_capacity=10, unit="hours")

    with pytest.raises(ValueError):
        resource.reserve(11)


def test_resource_rejects_negative_capacity():

    with pytest.raises(ValueError):
        Resource(name="Compute", total_capacity=-5, unit="hours")


# =====================================================
# Resource registry
# =====================================================


def test_resource_registry():

    registry = ResourceRegistry()

    resource = Resource(name="Compute", total_capacity=10, unit="hours")

    registry.register(resource)

    assert registry.count() == 1
    assert registry.get(resource.resource_id) == resource


# =====================================================
# Resource allocator
# =====================================================


def test_allocator_register_and_allocate():

    allocator = ResourceAllocator()

    resource = allocator.register_resource(
        name="Research Agent Pool",
        total_capacity=5,
        unit="agents",
        resource_type="agent",
    )

    allocation = allocator.allocate(
        resource_id=resource.resource_id,
        amount=2,
        mission_id="mission-1",
    )

    assert isinstance(allocation, ResourceAllocation)
    assert allocation.status == AllocationStatus.ALLOCATED
    assert allocator.available_capacity(resource.resource_id) == 3
    assert allocator.list_allocations_by_mission("mission-1") == [allocation]


def test_allocator_release_restores_capacity():

    allocator = ResourceAllocator()

    resource = allocator.register_resource(
        name="Compute",
        total_capacity=10,
        unit="hours",
    )

    allocation = allocator.allocate(
        resource_id=resource.resource_id,
        amount=6,
        mission_id="mission-1",
    )

    assert allocator.available_capacity(resource.resource_id) == 4

    allocator.release(allocation.allocation_id)

    assert allocator.available_capacity(resource.resource_id) == 10
    assert allocation.status == AllocationStatus.RELEASED


def test_allocator_prevents_overallocation():

    allocator = ResourceAllocator()

    resource = allocator.register_resource(
        name="Compute",
        total_capacity=5,
        unit="hours",
    )

    allocator.allocate(resource_id=resource.resource_id, amount=5)

    with pytest.raises(ValueError):
        allocator.allocate(resource_id=resource.resource_id, amount=1)


def test_allocator_stats():

    allocator = ResourceAllocator()

    resource = allocator.register_resource(
        name="Compute",
        total_capacity=10,
        unit="hours",
    )

    allocator.allocate(resource_id=resource.resource_id, amount=3)

    stats = allocator.stats()

    assert stats["total_resources"] == 1
    assert stats["total_allocations"] == 1
    assert stats["active_allocations"] == 1
