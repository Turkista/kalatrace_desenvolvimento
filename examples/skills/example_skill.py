"""
KALATRACE Example Skill

A minimal implementation used to validate
the KALATRACE Skill Framework lifecycle.

This Skill does not represent a real domain.
It exists only to test the Skill architecture.
"""

from skills.skill_interface import SkillInterface


class ExampleSkill(SkillInterface):
    """
    Example implementation of a KALATRACE Skill.
    """

    def __init__(self):
        super().__init__(
            name="example",
            version="1.0"
        )

        self.events_received = 0

    def initialize(self):
        """
        Initialize the Skill.
        """

        self.status = "initialized"

        print(
            "Example Skill initialized."
        )

    def activate(self):
        """
        Activate the Skill.
        """

        self.status = "active"

        print(
            "Example Skill activated."
        )

    def deactivate(self):
        """
        Deactivate the Skill.
        """

        self.status = "inactive"

        print(
            "Example Skill deactivated."
        )

    def process_event(
        self,
        event: dict
    ):
        """
        Process incoming events.
        """

        self.events_received += 1

        print(
            "Example Skill received event:"
        )

        print(event)
