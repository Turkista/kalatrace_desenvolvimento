"""
KALATRACE Command Context

Stores the execution environment
associated with a command.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import (
    datetime,
    timezone,
)

from typing import Any
from uuid import uuid4



class CommandContext:
    """
    Represents command execution context.

    Stores runtime information required
    during command execution.
    """


    def __init__(
        self,
        command_id: str,
        mission_id: str | None = None,
        executor: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        """
        Creates execution context.
        """


        if not isinstance(
            command_id,
            str,
        ):
            raise TypeError(
                "command_id must be a string."
            )


        if not command_id.strip():
            raise ValueError(
                "CommandContext requires a valid command_id."
            )


        self.context_id = str(
            uuid4()
        )


        self.command_id = (
            command_id.strip()
        )


        self.mission_id = mission_id

        self.executor = executor


        self.parameters: dict[str, Any] = (
            deepcopy(parameters)
            if parameters is not None
            else {}
        )


        self.metadata: dict[str, Any] = {}


        now = datetime.now(
            timezone.utc
        )


        self.created_at = now

        self.updated_at = now



    # =================================================
    # Internal utilities
    # =================================================


    def _touch(
        self,
    ) -> None:
        """
        Updates modification timestamp.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )



    # =================================================
    # Metadata
    # =================================================


    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Adds execution metadata.
        """


        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "Metadata key must be a string."
            )


        if not key.strip():
            raise ValueError(
                "Metadata key cannot be empty."
            )


        self.metadata[key.strip()] = value

        self._touch()



    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )



    def has_metadata(
        self,
        key: str,
    ) -> bool:

        return key in self.metadata



    # =================================================
    # Parameters
    # =================================================


    def set_parameter(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Defines execution parameter.
        """


        if not isinstance(
            key,
            str,
        ):
            raise TypeError(
                "Parameter key must be a string."
            )


        if not key.strip():
            raise ValueError(
                "Parameter key cannot be empty."
            )


        self.parameters[key.strip()] = value

        self._touch()



    def get_parameter(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.parameters.get(
            key,
            default,
        )



    def has_parameter(
        self,
        key: str,
    ) -> bool:

        return key in self.parameters



    # =================================================
    # Context operations
    # =================================================


    def clone(
        self,
    ) -> CommandContext:
        """
        Creates an independent copy
        of this execution context.
        """


        cloned = CommandContext(

            command_id=self.command_id,

            mission_id=self.mission_id,

            executor=self.executor,

            parameters=deepcopy(
                self.parameters
            ),

        )


        cloned.metadata = deepcopy(
            self.metadata
        )


        return cloned



    # =================================================
    # Serialization
    # =================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "context_id":
                self.context_id,

            "command_id":
                self.command_id,

            "mission_id":
                self.mission_id,

            "executor":
                self.executor,

            "parameters":
                self.parameters,

            "metadata":
                self.metadata,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

        }



    # =================================================
    # Representation
    # =================================================


    def __repr__(
        self,
    ) -> str:

        return (

            f"<CommandContext "
            f"id={self.context_id} "
            f"command={self.command_id} "
            f"executor={self.executor}>"

        )