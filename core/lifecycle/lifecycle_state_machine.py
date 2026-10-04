"""
KALATRACE Core

Lifecycle State Machine

Defines and validates lifecycle transitions
for executable KALATRACE components.
"""

from __future__ import annotations

from typing import ClassVar

from core.exceptions import (
    InvalidStateTransition,
)

from core.lifecycle.component_state import (
    ComponentState,
)


class LifecycleStateMachine:
    """
    Controls valid lifecycle transitions.

    Single source of truth for lifecycle rules.
    """


    _ALLOWED_TRANSITIONS: ClassVar[
        dict[
            ComponentState,
            frozenset[ComponentState],
        ]
    ] = {

        ComponentState.CREATED:
        frozenset({
            ComponentState.INITIALIZED,
            ComponentState.FAILED,
            ComponentState.DISPOSED,
        }),

        ComponentState.INITIALIZED:
        frozenset({
            ComponentState.STARTING,
            ComponentState.FAILED,
            ComponentState.DISPOSED,
        }),

        ComponentState.STARTING:
        frozenset({
            ComponentState.RUNNING,
            ComponentState.FAILED,
        }),

        ComponentState.RUNNING:
        frozenset({
            ComponentState.PAUSED,
            ComponentState.STOPPING,
            ComponentState.FAILED,
        }),

        ComponentState.PAUSED:
        frozenset({
            ComponentState.RUNNING,
            ComponentState.STOPPING,
            ComponentState.FAILED,
        }),

        ComponentState.STOPPING:
        frozenset({
            ComponentState.STOPPED,
            ComponentState.FAILED,
        }),

        ComponentState.STOPPED:
        frozenset({
            ComponentState.STARTING,
            ComponentState.DISPOSED,
        }),

        ComponentState.FAILED:
        frozenset({
            ComponentState.INITIALIZED,
            ComponentState.STOPPED,
            ComponentState.DISPOSED,
        }),

        ComponentState.DISPOSED:
        frozenset(),

        ComponentState.UNKNOWN:
        frozenset({
            ComponentState.CREATED,
        }),
    }



    _TERMINAL_STATES: ClassVar[
        frozenset[ComponentState]
    ] = frozenset({

        ComponentState.DISPOSED,

    })



    @classmethod
    def initial_state(
        cls,
    ) -> ComponentState:
        """
        Returns the default lifecycle state.
        """

        return ComponentState.CREATED



    @classmethod
    def is_valid_state(
        cls,
        state: ComponentState,
    ) -> bool:
        """
        Checks whether a lifecycle state
        is recognized.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            return False

        return state in cls._ALLOWED_TRANSITIONS



    @classmethod
    def can_transition(
        cls,
        current: ComponentState,
        target: ComponentState,
    ) -> bool:
        """
        Checks whether a transition is allowed.
        """

        if not isinstance(
            current,
            ComponentState,
        ):
            raise TypeError(
                "Current state must be a ComponentState."
            )

        if not isinstance(
            target,
            ComponentState,
        ):
            raise TypeError(
                "Target state must be a ComponentState."
            )

        return target in cls._ALLOWED_TRANSITIONS.get(
            current,
            frozenset(),
        )



    @classmethod
    def validate_transition(
        cls,
        current: ComponentState,
        target: ComponentState,
    ) -> None:
        """
        Validates a lifecycle transition.

        Raises InvalidStateTransition
        when transition is not allowed.
        """

        if not cls.can_transition(
            current,
            target,
        ):

            raise InvalidStateTransition(
                current,
                target,
            )



    @classmethod
    def allowed_transitions(
        cls,
        state: ComponentState,
    ) -> frozenset[ComponentState]:
        """
        Returns allowed next states.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )

        return cls._ALLOWED_TRANSITIONS.get(
            state,
            frozenset(),
        )



    @classmethod
    def is_terminal(
        cls,
        state: ComponentState,
    ) -> bool:
        """
        Indicates whether a state
        is terminal.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )

        return state in cls._TERMINAL_STATES



    @classmethod
    def is_recoverable(
        cls,
        state: ComponentState,
    ) -> bool:
        """
        Indicates whether a component
        may recover from this state.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )

        return state in {
            ComponentState.FAILED,
            ComponentState.STOPPED,
            ComponentState.PAUSED,
        }



    @classmethod
    def describe(
        cls,
        state: ComponentState,
    ) -> dict[str, object]:
        """
        Returns lifecycle state information.
        """

        if not isinstance(
            state,
            ComponentState,
        ):
            raise TypeError(
                "State must be a ComponentState."
            )

        return {

            "state":
                state.value,

            "allowed_transitions": [

                item.value

                for item
                in cls.allowed_transitions(
                    state
                )
            ],

            "terminal":
                cls.is_terminal(
                    state
                ),

            "recoverable":
                cls.is_recoverable(
                    state
                ),
        }