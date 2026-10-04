"""
KALATRACE Core

Component State

Defines the lifecycle states shared by executable
components throughout the KALATRACE architecture.
"""

from __future__ import annotations

from enum import Enum


class ComponentState(str, Enum):
    """
    Standard lifecycle states for executable
    KALATRACE components.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    STARTING = "starting"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"

    DISPOSED = "disposed"

    UNKNOWN = "unknown"


    # =================================================
    # State classification
    # =================================================


    @property
    def is_active(
        self,
    ) -> bool:
        """
        Indicates whether the component
        is currently active.
        """

        return self in {
            ComponentState.STARTING,
            ComponentState.RUNNING,
            ComponentState.PAUSED,
        }


    @property
    def is_initialized(
        self,
    ) -> bool:
        """
        Indicates whether the component
        completed initialization.
        """

        return self in {
            ComponentState.INITIALIZED,
            ComponentState.STARTING,
            ComponentState.RUNNING,
            ComponentState.PAUSED,
            ComponentState.STOPPING,
            ComponentState.STOPPED,
        }


    @property
    def is_running(
        self,
    ) -> bool:
        """
        Indicates whether the component
        is executing.
        """

        return self == ComponentState.RUNNING


    @property
    def is_terminal(
        self,
    ) -> bool:
        """
        Indicates whether this state
        represents a final lifecycle state.
        """

        return self in {
            ComponentState.STOPPED,
            ComponentState.FAILED,
            ComponentState.DISPOSED,
        }


    @property
    def is_failed(
        self,
    ) -> bool:
        """
        Indicates whether the component
        entered failure state.
        """

        return self == ComponentState.FAILED


    @property
    def is_disposed(
        self,
    ) -> bool:
        """
        Indicates whether resources
        were released.
        """

        return self == ComponentState.DISPOSED


    @property
    def is_recoverable(
        self,
    ) -> bool:
        """
        Indicates whether the component
        may recover from this state.
        """

        return self in {
            ComponentState.FAILED,
            ComponentState.STOPPED,
            ComponentState.PAUSED,
        }


    # =================================================
    # Transition permissions
    # =================================================


    @property
    def can_start(
        self,
    ) -> bool:
        """
        Indicates whether execution
        may start.
        """

        return self in {
            ComponentState.CREATED,
            ComponentState.INITIALIZED,
            ComponentState.STOPPED,
        }


    @property
    def can_stop(
        self,
    ) -> bool:
        """
        Indicates whether execution
        may stop.
        """

        return self in {
            ComponentState.STARTING,
            ComponentState.RUNNING,
            ComponentState.PAUSED,
        }


    def can_transition_to(
        self,
        target: ComponentState,
    ) -> bool:
        """
        Validates lifecycle transition.

        LifecycleStateMachine remains the
        authoritative transition controller.
        """

        if not isinstance(
            target,
            ComponentState,
        ):
            raise TypeError(
                "Target must be a ComponentState."
            )


        allowed = {

            ComponentState.CREATED: {
                ComponentState.INITIALIZED,
                ComponentState.FAILED,
            },

            ComponentState.INITIALIZED: {
                ComponentState.STARTING,
                ComponentState.FAILED,
            },

            ComponentState.STARTING: {
                ComponentState.RUNNING,
                ComponentState.FAILED,
            },

            ComponentState.RUNNING: {
                ComponentState.PAUSED,
                ComponentState.STOPPING,
                ComponentState.FAILED,
            },

            ComponentState.PAUSED: {
                ComponentState.RUNNING,
                ComponentState.STOPPING,
                ComponentState.FAILED,
            },

            ComponentState.STOPPING: {
                ComponentState.STOPPED,
                ComponentState.FAILED,
            },

            ComponentState.STOPPED: {
                ComponentState.STARTING,
                ComponentState.DISPOSED,
            },

            ComponentState.FAILED: {
                ComponentState.DISPOSED,
            },

            ComponentState.DISPOSED: set(),

            ComponentState.UNKNOWN: set(),
        }


        return target in allowed.get(
            self,
            set(),
        )