"""
KALATRACE Resource Registry

Stores and manages resources available for allocation
by the Resource Allocator.
"""

from __future__ import annotations

from .resource import Resource


class ResourceRegistry:
    """
    Registry responsible for resource storage.
    """

    def __init__(self) -> None:
        """
        Initializes registry.
        """

        self._resources: dict[str, Resource] = {}

    # =================================================
    # Registration
    # =================================================

    def register(self, resource: Resource) -> None:
        """
        Registers a resource.
        """

        if not isinstance(resource, Resource):
            raise TypeError(
                "Only Resource instances can be registered."
            )

        if resource.resource_id in self._resources:
            raise ValueError(
                f"Resource already registered: "
                f"{resource.resource_id}"
            )

        self._resources[resource.resource_id] = resource

    def remove(self, resource_id: str) -> None:
        """
        Removes a resource.
        """

        if not isinstance(resource_id, str):
            raise TypeError(
                "resource_id must be a string."
            )

        self._resources.pop(resource_id, None)

    # =================================================
    # Retrieval
    # =================================================

    def get(self, resource_id: str) -> Resource | None:
        """
        Retrieves resource by id.
        """

        if not isinstance(resource_id, str):
            raise TypeError(
                "resource_id must be a string."
            )

        return self._resources.get(resource_id)

    def exists(self, resource_id: str) -> bool:
        """
        Checks resource existence.
        """

        if not isinstance(resource_id, str):
            raise TypeError(
                "resource_id must be a string."
            )

        return resource_id in self._resources

    # =================================================
    # Queries
    # =================================================

    def list_all(self) -> list[Resource]:
        """
        Returns all resources.
        """

        return list(self._resources.values())

    def list_by_type(self, resource_type: str) -> list[Resource]:
        """
        Returns resources filtered by type.
        """

        normalized = (
            resource_type.strip().upper()
            if isinstance(resource_type, str)
            else resource_type
        )

        return [
            resource
            for resource in self._resources.values()
            if resource.resource_type == normalized
        ]

    # =================================================
    # Information
    # =================================================

    def count(self) -> int:
        """
        Returns total resource count.
        """

        return len(self._resources)

    def stats(self) -> dict:
        """
        Returns registry statistics.
        """

        return {

            "total_resources": self.count(),

            "total_capacity": sum(
                resource.total_capacity
                for resource in self._resources.values()
            ),

            "total_allocated": sum(
                resource.allocated
                for resource in self._resources.values()
            ),

            "registry": "ResourceRegistry",

        }

    def to_dict(self) -> dict:
        """
        Exports registry state.
        """

        return {
            "resources": [
                resource.to_dict()
                for resource in self._resources.values()
            ]
        }

    def clear(self) -> None:
        """
        Clears all registered resources.
        """

        self._resources.clear()
