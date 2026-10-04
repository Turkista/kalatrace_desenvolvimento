"""
KALATRACE Skill Interface

Defines the standard contract that every KALATRACE Skill must implement.

A Skill is a specialized application module that extends the KALATRACE
Core with domain-specific capabilities while maintaining a common lifecycle.
"""

from abc import ABC, abstractmethod
from datetime import datetime, UTC


class SkillInterface(ABC):
    """
    Abstract base class for all KALATRACE Skills.

    Every Skill must implement:
    - initialization
    - activation
    - deactivation
    - event processing
    """

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.status = "created"
        self.created_at = datetime.now(UTC)

    @abstractmethod
    def initialize(self):
        """
        Prepare the Skill environment.

        Examples:
        - load configurations
        - connect external services
        - prepare internal resources
        """
        pass

    @abstractmethod
    def activate(self):
        """
        Activate the Skill.

        After activation, the Skill can receive events
        and communicate with the KALATRACE Core.
        """
        pass

    @abstractmethod
    def deactivate(self):
        """
        Safely deactivate the Skill.

        Examples:
        - close connections
        - save state
        - release resources
        """
        pass

    @abstractmethod
    def process_event(self, event: dict):
        """
        Process events received by the Skill.

        Events may come from:
        - external systems
        - sensors
        - users
        - other KALATRACE components
        """
        pass

    def get_info(self):
        """
        Returns basic Skill metadata.
        """

        return {
            "name": self.name,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }