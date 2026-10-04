"""
KALATRACE Command History

Tracks command lifecycle events
for auditability and replay.
"""


from __future__ import annotations

from datetime import (
    datetime,
    UTC,
)

from typing import Any



class CommandHistory:
    """
    Stores chronological command events.

    Provides traceability information
    about command lifecycle execution.
    """



    def __init__(
        self,
        command_id: str,
    ) -> None:
        """
        Initializes command history.
        """


        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        command_id = command_id.strip()


        if not command_id:
            raise ValueError(
                "CommandHistory requires a valid command_id."
            )


        self.command_id = command_id


        self.events: list[
            dict[str, Any]
        ] = []



    # =================================================
    # Events
    # =================================================


    def add_event(
        self,
        event: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Adds lifecycle event.
        """


        if not isinstance(
            event,
            str,
        ):
            raise TypeError(
                "event must be a string."
            )


        event = event.strip()


        if not event:
            raise ValueError(
                "History event cannot be empty."
            )


        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary."
            )


        self.events.append(

            {

                "event":
                    event,


                "metadata":
                    metadata
                    if metadata is not None
                    else {},


                "timestamp":
                    datetime.now(
                        UTC
                    ),

            }

        )



    # =================================================
    # Queries
    # =================================================


    def last_event(
        self,
    ) -> dict[str, Any] | None:
        """
        Returns latest event.
        """


        if not self.events:
            return None


        return self.events[-1]



    def all_events(
        self,
    ) -> list[dict[str, Any]]:
        """
        Returns complete history.
        """


        return list(
            self.events
        )



    def count(
        self,
    ) -> int:
        """
        Returns event count.
        """

        return len(
            self.events
        )



    def clear(
        self,
    ) -> None:
        """
        Clears stored history.
        """

        self.events.clear()



    # =================================================
    # Serialization
    # =================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Converts history into dictionary.
        """

        return {

            "command_id":
                self.command_id,


            "events":
                self.all_events(),

        }



    # =================================================
    # Representation
    # =================================================


    def __repr__(
        self,
    ) -> str:

        return (
            f"<CommandHistory "
            f"command={self.command_id} "
            f"events={len(self.events)}>"
        )