"""
KALATRACE Core

Repository Contract

Defines the abstraction for persistence repositories
within the KALATRACE architecture.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


EntityType = TypeVar(
    "EntityType"
)

IdentifierType = TypeVar(
    "IdentifierType"
)


class RepositoryContract(
    ABC,
    Generic[EntityType, IdentifierType],
):
    """
    Base contract for repositories.

    A repository provides an abstraction layer between
    domain entities and persistence mechanisms.
    """


    @abstractmethod
    def save(
        self,
        entity: EntityType,
    ) -> EntityType:
        """
        Stores or updates an entity.
        """
        ...


    @abstractmethod
    def find_by_id(
        self,
        identifier: IdentifierType,
    ) -> EntityType | None:
        """
        Retrieves an entity by identifier.
        """
        ...


    @abstractmethod
    def delete(
        self,
        identifier: IdentifierType,
    ) -> bool:
        """
        Removes an entity.

        Returns True if deletion succeeded.
        """
        ...


    @abstractmethod
    def exists(
        self,
        identifier: IdentifierType,
    ) -> bool:
        """
        Checks whether an entity exists.
        """
        ...


    @abstractmethod
    def list_all(
        self,
    ) -> list[EntityType]:
        """
        Returns all available entities.
        """
        ...


    def count(
        self,
    ) -> int:
        """
        Returns entity count.

        Default implementation.
        """

        return len(
            self.list_all()
        )


    def query(
        self,
        criteria: dict,
    ) -> list[EntityType]:
        """
        Searches entities using criteria.

        Default implementation.
        """

        return []