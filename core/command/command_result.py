"""
KALATRACE Command Result

Represents the output generated after
a command execution.
"""


from __future__ import annotations

from datetime import (
    datetime,
    UTC,
)

from typing import Any

from uuid import uuid4



class CommandResult:
    """
    Stores command execution results.

    Represents the final output produced
    by a command executor.
    """



    def __init__(
        self,
        command_id: str,
        success: bool,
        message: str = "",
        data: dict[str, Any] | None = None,
        executor: str | None = None,
        confidence: float = 0.0,
    ) -> None:
        """
        Creates execution result.
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
                "CommandResult requires a valid command_id."
            )


        if not isinstance(
            success,
            bool,
        ):
            raise TypeError(
                "success must be a boolean."
            )


        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Confidence must be between 0.0 and 1.0."
            )


        if data is not None and not isinstance(
            data,
            dict,
        ):
            raise TypeError(
                "data must be a dictionary."
            )


        if executor is not None and not isinstance(
            executor,
            str,
        ):
            raise TypeError(
                "executor must be a string."
            )



        self.result_id = str(
            uuid4()
        )


        self.command_id = command_id


        self.success = success


        self.message = (
            message.strip()
            if isinstance(message, str)
            else ""
        )


        self.data = (
            data
            if data is not None
            else {}
        )


        self.executor = (
            executor.strip()
            if executor
            else None
        )


        self.confidence = confidence


        self.created_at = datetime.now(
            UTC
        )



    # =================================================
    # Factory Methods
    # =================================================


    @classmethod
    def success_result(
        cls,
        command_id: str,
        message: str = "",
        data: dict[str, Any] | None = None,
        executor: str | None = None,
        confidence: float = 1.0,
    ) -> CommandResult:

        return cls(
            command_id=command_id,
            success=True,
            message=message,
            data=data,
            executor=executor,
            confidence=confidence,
        )



    @classmethod
    def failure_result(
        cls,
        command_id: str,
        message: str = "",
        data: dict[str, Any] | None = None,
        executor: str | None = None,
        confidence: float = 0.0,
    ) -> CommandResult:

        return cls(
            command_id=command_id,
            success=False,
            message=message,
            data=data,
            executor=executor,
            confidence=confidence,
        )



    # =================================================
    # Status Helpers
    # =================================================


    @property
    def is_successful(
        self,
    ) -> bool:

        return self.success



    @property
    def is_failure(
        self,
    ) -> bool:

        return not self.success



    # =================================================
    # Serialization
    # =================================================


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {

            "result_id":
                self.result_id,

            "command_id":
                self.command_id,

            "success":
                self.success,

            "message":
                self.message,

            "data":
                self.data,

            "executor":
                self.executor,

            "confidence":
                self.confidence,

            "created_at":
                self.created_at,

        }



    def __repr__(
        self,
    ) -> str:

        return (
            f"<CommandResult "
            f"command={self.command_id} "
            f"success={self.success}>"
        )