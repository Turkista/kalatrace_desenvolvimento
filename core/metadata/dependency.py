"""
KALATRACE Core

Dependency Metadata

Defines immutable metadata describing dependencies
between system components.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.metadata.version import Version


class DependencyType(Enum):
    """
    Categories of component dependencies.
    """

    REQUIRED = "required"
    OPTIONAL = "optional"
    DEVELOPMENT = "development"


@dataclass(
    frozen=True,
    slots=True,
)
class Dependency:
    """
    Immutable dependency declaration.

    Used by the Registry, Runtime and ComponentLoader
    to resolve component loading order and compatibility.
    """

    identifier: str

    minimum_version: Version

    maximum_version: Version | None = None

    dependency_type: DependencyType = (
        DependencyType.REQUIRED
    )

    description: str = ""


    def __post_init__(self) -> None:
        """
        Validate dependency metadata.
        """

        identifier = self.identifier.strip()

        description = self.description.strip()


        if not identifier:
            raise ValueError(
                "Dependency identifier cannot be empty."
            )


        if self.minimum_version is None:
            raise ValueError(
                "Minimum version cannot be None."
            )


        if (
            self.maximum_version is not None
            and self.maximum_version < self.minimum_version
        ):
            raise ValueError(
                "Maximum version cannot be lower than minimum version."
            )


        object.__setattr__(
            self,
            "identifier",
            identifier,
        )

        object.__setattr__(
            self,
            "description",
            description,
        )


    def is_satisfied_by(
        self,
        version: Version,
    ) -> bool:
        """
        Checks whether a version satisfies this dependency.
        """

        if version < self.minimum_version:
            return False


        if (
            self.maximum_version is not None
            and version > self.maximum_version
        ):
            return False


        return True


    def __str__(
        self,
    ) -> str:
        """
        Returns a readable dependency description.
        """

        if self.maximum_version is None:
            return (
                f"{self.identifier} "
                f">={self.minimum_version}"
            )


        return (
            f"{self.identifier} "
            f">={self.minimum_version} "
            f"<= {self.maximum_version}"
        )