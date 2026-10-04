"""
KALATRACE Mission Timeline

Provides temporal traceability for missions.

A timeline stores operational events
generated during mission execution.
"""


from datetime import datetime, UTC
from uuid import uuid4



class MissionEvent:
    """
    Represents a single mission timeline event.
    """


    def __init__(
        self,
        event_type: str,
        description: str,
        source: str | None = None,
        metadata: dict | None = None,
    ):
        """
        Creates a mission event.
        """


        if not event_type or not event_type.strip():
            raise ValueError(
                "Mission event type cannot be empty."
            )


        if not description or not description.strip():
            raise ValueError(
                "Mission event description cannot be empty."
            )


        self.event_id = str(
            uuid4()
        )


        self.timestamp = datetime.now(
            UTC
        )


        self.event_type = (
            event_type.strip()
        )


        self.description = (
            description.strip()
        )


        self.source = (
            source.strip()
            if source
            else None
        )


        self.metadata = (
            dict(metadata)
            if metadata
            else {}
        )



    def to_dict(
        self,
    ) -> dict:
        """
        Converts event into serializable structure.
        """


        return {

            "event_id":
                self.event_id,

            "timestamp":
                self.timestamp,

            "event_type":
                self.event_type,

            "description":
                self.description,

            "source":
                self.source,

            "metadata":
                self.metadata,

        }



    def __repr__(
        self,
    ) -> str:

        return (
            f"<MissionEvent "
            f"type={self.event_type} "
            f"id={self.event_id}>"
        )




class MissionTimeline:
    """
    Stores mission history.
    """


    def __init__(
        self,
    ):
        """
        Initialize timeline storage.
        """


        self.events: list[MissionEvent] = []



    def add_event(
        self,
        event_type: str,
        description: str,
        source: str | None = None,
        metadata: dict | None = None,
    ) -> MissionEvent:
        """
        Adds an event to timeline.
        """


        event = MissionEvent(
            event_type=event_type,
            description=description,
            source=source,
            metadata=metadata,
        )


        self.events.append(
            event
        )


        return event



    def get_events(
        self,
    ) -> list[MissionEvent]:
        """
        Returns all timeline events.
        """


        return list(
            self.events
        )



    def get_by_type(
        self,
        event_type: str,
    ) -> list[MissionEvent]:
        """
        Returns events filtered by type.
        """


        return [

            event

            for event
            in self.events

            if event.event_type == event_type

        ]



    def latest(
        self,
    ) -> MissionEvent | None:
        """
        Returns most recent event.
        """


        if not self.events:
            return None


        return self.events[-1]



    def count(
        self,
    ) -> int:
        """
        Returns number of events.
        """


        return len(
            self.events
        )



    def history(
        self,
    ) -> list[dict]:
        """
        Returns complete timeline history.
        """


        return [

            event.to_dict()

            for event
            in self.events

        ]



    def clear(
        self,
    ) -> None:
        """
        Removes all timeline events.
        """


        self.events.clear()



    def to_dict(
        self,
    ) -> dict:
        """
        Exports timeline state.
        """


        return {

            "events":
                self.history(),

            "count":
                self.count(),

        }



    def __repr__(
        self,
    ) -> str:

        return (
            f"<MissionTimeline "
            f"events={self.count()}>"
        )