"""
KALATRACE Resource Allocator

Public resource allocation API.

This package implements the "Resource Allocation"
responsibility of the Command & Mission Center: registering
allocatable resources (compute, agents, budget, etc.),
granting capacity to missions, and releasing it back.

Provides:

- Resource entity (capacity accounting)
- ResourceAllocation entity (a single grant record)
- Resource registry
- Resource Allocator facade
"""

from __future__ import annotations


# =================================================
# Core Entities
# =================================================

from .resource import Resource

from .resource_allocation import (
    ResourceAllocation,
    AllocationStatus,
)


# =================================================
# Registry
# =================================================

from .resource_registry import ResourceRegistry


# =================================================
# Facade
# =================================================

from .resource_allocator import ResourceAllocator


__all__ = [

    "Resource",

    "ResourceAllocation",

    "AllocationStatus",

    "ResourceRegistry",

    "ResourceAllocator",

]
