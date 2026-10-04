"""
KALATRACE Command Dispatcher

Responsible for routing commands
to execution targets.
"""


from __future__ import annotations

from .command import Command



class CommandDispatcher:
    """
    Dispatches commands to executors.

    Executors may represent:
    - Agents
    - Engines
    - Skills
    - External workers

    Future versions should replace
    generic objects with ExecutorContract.
    """



    def __init__(
        self,
    ) -> None:

        self.executors: dict[
            str,
            object,
        ] = {}



    # =================================================
    # Executor Registration
    # =================================================

    def register_executor(
        self,
        name: str,
        executor: object,
    ) -> None:
        """
        Registers an execution target.
        """


        if not isinstance(
            name,
            str,
        ):

            raise TypeError(
                "Executor name must be a string."
            )


        name = name.strip()


        if not name:

            raise ValueError(
                "Executor name cannot be empty."
            )


        if executor is None:

            raise ValueError(
                "Executor cannot be None."
            )


        self.executors[
            name
        ] = executor



    def unregister_executor(
        self,
        name: str,
    ) -> None:
        """
        Removes executor.
        """


        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Executor name must be a string."
            )


        self.executors.pop(
            name.strip(),
            None,
        )



    # =================================================
    # Dispatch
    # =================================================

    def dispatch(
        self,
        command: Command,
        target: str,
    ) -> object:
        """
        Sends command to executor.
        """


        if not isinstance(
            command,
            Command,
        ):

            raise TypeError(
                "dispatch requires a Command instance."
            )


        if not isinstance(
            target,
            str,
        ):

            raise TypeError(
                "Executor target must be a string."
            )


        target = target.strip()


        if not target:

            raise ValueError(
                "Executor target cannot be empty."
            )


        executor = self.executors.get(
            target
        )


        if executor is None:

            raise ValueError(
                f"Executor not found: {target}"
            )


        if not hasattr(
            executor,
            "execute",
        ):

            raise TypeError(
                f"Executor '{target}' does not implement execute()."
            )



        command.add_history(
            f"Dispatched to {target}"
        )


        try:

            result = executor.execute(
                command
            )


        except Exception as exc:

            command.add_history(
                f"Execution failed on {target}: {exc}"
            )

            raise



        command.add_history(
            f"Execution returned from {target}"
        )


        return result



    # =================================================
    # Information
    # =================================================

    def available_executors(
        self,
    ) -> list[str]:
        """
        Returns registered executors.
        """

        return list(
            self.executors.keys()
        )



    def has_executor(
        self,
        name: str,
    ) -> bool:
        """
        Checks executor availability.
        """


        if not isinstance(
            name,
            str,
        ):
            return False


        return (
            name.strip()
            in
            self.executors
        )