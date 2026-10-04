"""
KALATRACE Core

Base Component

Provides the common infrastructure shared by executable
KALATRACE components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..lifecycle.component_state import ComponentState
from ..lifecycle.lifecycle_state_machine import LifecycleStateMachine
from ..metadata.component_metadata import ComponentMetadata


class BaseComponent(ABC):
    """
    Base class for executable KALATRACE components.

    Provides common lifecycle state management.

    Metadata definition is delegated to subclasses.
    Component registration, persistence, and discovery
    are responsibilities of higher-level services.
    """

    def __init__(self) -> None:
        self._state = ComponentState.CREATED

    @property
    @abstractmethod
    def metadata(self) -> ComponentMetadata:
        """
        Returns the descriptive metadata of this component.
        """
        ...

    @property
    def state(self) -> ComponentState:
        """
        Returns the current lifecycle state.
        """
        return self._state

    @property
    def is_running(self) -> bool:
        """
        Indicates whether the component is active.
        """
        return self._state.is_active

    def _transition_to(
        self,
        target: ComponentState,
    ) -> None:
        """
        Performs a validated lifecycle transition.

        Intended for internal framework usage.
        """

        LifecycleStateMachine.validate_transition(
            self._state,
            target,
        )

        self._state = target