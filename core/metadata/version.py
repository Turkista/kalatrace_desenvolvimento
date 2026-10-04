"""
KALATRACE Core

Version Metadata

Defines immutable semantic version information used throughout the
KALATRACE architecture for component compatibility, dependency
resolution and version comparison.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    order=True,
)
class Version:
    """
    Immutable Semantic Version.

    Represents a semantic version following the format:

        MAJOR.MINOR.PATCH

    Examples:
        1.0.0
        2.3.5
    """

    major: int

    minor: int

    patch: int


    def __post_init__(self) -> None:
        """
        Validates version values.
        """

        if self.major < 0:
            raise ValueError(
                "Major version cannot be negative."
            )

        if self.minor < 0:
            raise ValueError(
                "Minor version cannot be negative."
            )

        if self.patch < 0:
            raise ValueError(
                "Patch version cannot be negative."
            )


    def __str__(self) -> str:
        """
        Returns the semantic version string.
        """

        return (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )


    def __repr__(self) -> str:
        """
        Returns a developer-friendly representation.
        """

        return f'Version("{self}")'


    def to_tuple(
        self,
    ) -> tuple[int, int, int]:
        """
        Returns the version as a tuple.

        Example:
            (1, 2, 3)
        """

        return (
            self.major,
            self.minor,
            self.patch,
        )


    def is_compatible(
        self,
        other: Version,
        *,
        major_only: bool = True,
    ) -> bool:
        """
        Determines whether two versions are compatible.

        Parameters
        ----------
        other:
            Version to compare against.

        major_only:
            If True, compatibility requires only the same
            major version.

            If False, compatibility requires:

            - Same major version.
            - This version is greater than or equal to
              the required version.
        """

        if major_only:
            return self.major == other.major

        return (
            self.major == other.major
            and self >= other
        )


    def bump_major(
        self,
    ) -> Version:
        """
        Returns the next major version.

        Example:
            1.4.8 -> 2.0.0
        """

        return Version(
            self.major + 1,
            0,
            0,
        )


    def bump_minor(
        self,
    ) -> Version:
        """
        Returns the next minor version.

        Example:
            1.4.8 -> 1.5.0
        """

        return Version(
            self.major,
            self.minor + 1,
            0,
        )


    def bump_patch(
        self,
    ) -> Version:
        """
        Returns the next patch version.

        Example:
            1.4.8 -> 1.4.9
        """

        return Version(
            self.major,
            self.minor,
            self.patch + 1,
        )


    @classmethod
    def parse(
        cls,
        value: str,
    ) -> Version:
        """
        Creates a Version from a semantic version string.

        Accepts:

            1.2.3
            v1.2.3

        Examples:
            Version.parse("1.2.3")
            Version.parse("v1.2.3")
        """

        value = value.strip()

        if value.startswith("v"):
            value = value[1:]


        parts = value.split(".")


        if len(parts) != 3:
            raise ValueError(
                "Version must follow the format "
                "'MAJOR.MINOR.PATCH'."
            )


        try:

            major, minor, patch = (
                int(part)
                for part in parts
            )

        except ValueError as exc:

            raise ValueError(
                "Version components must be integers."
            ) from exc


        return cls(
            major=major,
            minor=minor,
            patch=patch,
        )


#
# Commonly used versions.
#

ZERO_VERSION = Version(
    0,
    0,
    0,
)


INITIAL_VERSION = Version(
    1,
    0,
    0,
)