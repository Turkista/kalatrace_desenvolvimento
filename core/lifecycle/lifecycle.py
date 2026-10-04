"""
KALATRACE Core

Lifecycle

Default lifecycle implementation shared by
executable KALATRACE components.
"""

from __future__ import annotations

from abc import abstractmethod

from core.contracts.lifecycle_contract import (
    LifecycleContract,
)

from core.lifecycle.component_state import (
    ComponentState,
)

from core.lifecycle.lifecycle_state_machine import (
    LifecycleStateMachine,
)


class Lifecycle(
    LifecycleContract,
):
    """
    Default lifecycle implementation.

    Responsible for:

    - Maintaining component state
    - Validating lifecycle transitions
    - Providing lifecycle primitives
    """


    def __init__(
        self,
    ) -> None:

        self._state = (
            LifecycleStateMachine.initial_state()
        )



    # =================================================
    # State access
    # =================================================


    @property
    def state(
        self,
    ) -> ComponentState:
        """
        Returns current lifecycle state.
        """

        return self._state



    @property
    def is_running(
        self,
    ) -> bool:
        """
        Indicates whether component
        is currently executing.
        """

        return (
            self._state
            == ComponentState.RUNNING
        )



    @property
    def is_active(
        self,
    ) -> bool:
        """
        Indicates whether component
        is in an active lifecycle phase.
        """

        return self._state.is_active



    @property
    def is_terminal(
        self,
    ) -> bool:
        """
        Indicates whether component
        reached a terminal state.
        """

        return self._state.is_terminal



    # =================================================
    # State transition
    # =================================================


    def set_state(
        self,
        state: ComponentState,
    ) -> None:
        """
        Changes the current lifecycle state after
        validating the requested transition.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )


        if state == self._state:
            return


        LifecycleStateMachine.validate_transition(
            self._state,
            state,
        )


        self._state = state



    def can_transition_to(
        self,
        state: ComponentState,
    ) -> bool:
        """
        Checks whether transition is allowed.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )


        return LifecycleStateMachine.can_transition(
            self._state,
            state,
        )



    # =================================================
    # Lifecycle operations
    # =================================================


    @abstractmethod
    def initialize(
        self,
    ) -> None:
        """
        Initializes component resources.
        """
        ...



    @abstractmethod
    def start(
        self,
    ) -> None:
        """
        Starts component execution.
        """
        ...



    @abstractmethod
    def stop(
        self,
    ) -> None:
        """
        Stops component execution.
        """
        ...



    def shutdown(
        self,
    ) -> None:
        """
        Releases resources.

        Shutdown is idempotent.
        """


        if self._state == (
            ComponentState.DISPOSED
        ):
            return


        if LifecycleStateMachine.can_transition(
            self._state,
            ComponentState.DISPOSED,
        ):

            self.set_state(
                ComponentState.DISPOSED
            )