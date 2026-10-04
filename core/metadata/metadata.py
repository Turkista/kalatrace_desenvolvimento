"""
KALATRACE Core

Metadata

Base metadata shared by KALATRACE components.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .version import Version


@dataclass(slots=True)
class Metadata:
    """
    Base metadata shared by KALATRACE components.
    """

    identifier: str

    name: str

    version: Version = field(
        default_factory=lambda: Version(1, 0, 0)
    )

    description: str = ""

    tags: list[str] = field(
        default_factory=list
    )

    attributes: dict[str, str] = field(
        default_factory=dict
    )


    def __post_init__(self) -> None:
        """
        Validate and normalize metadata.
        """

        self.identifier = (
            self.identifier.strip()
        )

        self.name = (
            self.name.strip()
        )

        self.description = (
            self.description.strip()
        )


        if not self.identifier:
            raise ValueError(
                "Metadata identifier cannot be empty."
            )

        if not self.name:
            raise ValueError(
                "Metadata name cannot be empty."
            )


        self.tags = [
            tag.strip()
            for tag in self.tags
            if tag.strip()
        ]


        self.attributes = {
            key.strip(): value.strip()
            for key, value in self.attributes.items()
            if key.strip()
        }


    def has_tag(
        self,
        tag: str,
    ) -> bool:
        """
        Checks whether metadata contains a tag.
        """

        return tag in self.tags


    def add_tag(
        self,
        tag: str,
    ) -> None:
        """
        Adds a tag if it does not already exist.
        """

        normalized_tag = tag.strip()

        if (
            normalized_tag
            and normalized_tag not in self.tags
        ):
            self.tags.append(
                normalized_tag
            )


    def get_attribute(
        self,
        key: str,
        default: str | None = None,
    ) -> str | None:
        """
        Returns an attribute value.
        """

        return self.attributes.get(
            key,
            default,
        )


    def set_attribute(
        self,
        key: str,
        value: str,
    ) -> None:
        """
        Sets a metadata attribute.
        """

        normalized_key = key.strip()

        if not normalized_key:
            raise ValueError(
                "Metadata attribute key cannot be empty."
            )

        self.attributes[normalized_key] = (
            value.strip()
        )