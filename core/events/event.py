"""
KALATRACE Core

Event

Defines the immutable event object used
for communication between KALATRACE components.
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)

from datetime import (
    datetime,
    timezone,
)

from uuid import (
    UUID,
    uuid4,
)

from typing import (
    Any,
)

from core.events.event_priority import (
    EventPriority,
)

from core.events.event_type import (
    EventType,
)



@dataclass(
    frozen=True,
    slots=True,
)
class Event:
    """
    Immutable event message exchanged
    through the KALATRACE EventBus.

    Events provide:

    - event identification;
    - event classification;
    - source tracking;
    - payload transport;
    - priority control;
    - schema versioning.
    """


    event_type: EventType


    source_id: str


    payload: dict[str, Any] = field(
        default_factory=dict
    )


    priority: EventPriority = (
        EventPriority.NORMAL
    )


    schema_version: str = "1.0"


    event_id: UUID = field(
        default_factory=uuid4
    )


    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



    def __post_init__(self) -> None:
        """
        Validates event consistency.
        """


        if self.event_type is None:
            raise ValueError(
                "Event type is required."
            )


        if not isinstance(
            self.event_type,
            EventType,
        ):
            raise TypeError(
                "Event type must be EventType."
            )


        if self.priority is None:
            raise ValueError(
                "Event priority is required."
            )


        if not isinstance(
            self.priority,
            EventPriority,
        ):
            raise TypeError(
                "Event priority must be EventPriority."
            )


        if self.source_id is None:
            raise ValueError(
                "Event source_id is required."
            )


        if not isinstance(
            self.source_id,
            str,
        ):
            raise TypeError(
                "Event source_id must be a string."
            )


        normalized_source = (
            self.source_id.strip()
        )


        if not normalized_source:
            raise ValueError(
                "Event source_id cannot be empty."
            )



        if self.schema_version is None:
            raise ValueError(
                "Event schema_version is required."
            )


        if not isinstance(
            self.schema_version,
            str,
        ):
            raise TypeError(
                "Event schema_version must be a string."
            )


        normalized_schema = (
            self.schema_version.strip()
        )


        if not normalized_schema:
            raise ValueError(
                "Event schema_version cannot be empty."
            )



        if not isinstance(
            self.payload,
            dict,
        ):
            raise TypeError(
                "Event payload must be a dictionary."
            )


        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "Event metadata must be a dictionary."
            )



        object.__setattr__(
            self,
            "source_id",
            normalized_source,
        )


        object.__setattr__(
            self,
            "schema_version",
            normalized_schema,
        )



    def with_metadata(
        self,
        **metadata: Any,
    ) -> Event:
        """
        Creates a new event instance
        with additional metadata.

        Maintains immutability.
        """


        updated_metadata = {
            **self.metadata,
            **metadata,
        }


        return Event(

            event_type=self.event_type,

            source_id=self.source_id,

            payload=self.payload,

            priority=self.priority,

            schema_version=self.schema_version,

            event_id=self.event_id,

            created_at=self.created_at,

            metadata=updated_metadata,

        )



    def has_payload(
        self,
        key: str,
    ) -> bool:
        """
        Checks whether payload contains
        a specific key.
        """


        return key in self.payload



    def get_payload(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieves payload data.
        """


        return self.payload.get(
            key,
            default,
        )



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serializes event information.
        """


        return {

            "event_id":
                str(
                    self.event_id
                ),

            "event_type":
                self.event_type.value,

            "source_id":
                self.source_id,

            "priority":
                self.priority.name,

            "schema_version":
                self.schema_version,

            "created_at":
                self.created_at.isoformat(),

            "payload":
                self.payload,

            "metadata":
                self.metadata,

        }