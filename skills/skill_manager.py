"""
KALATRACE Skill Manager

Responsible for managing the lifecycle of KALATRACE Skills.

The Skill Manager handles:
- loading Skills
- initializing Skills
- activating Skills
- deactivating Skills
- monitoring Skill status

It acts as the execution controller for the Skill ecosystem.
"""

from skills.skill_registry import SkillRegistry


class SkillManager:
    """
    Controls the lifecycle of installed Skills.
    """

    def __init__(self):
        self.registry = SkillRegistry()
        self.loaded_skills = {}

    def install_skill(
        self,
        skill_name: str,
        skill_instance,
        version: str,
        description: str = ""
    ):
        """
        Install a new Skill into the KALATRACE ecosystem.

        Args:
            skill_name:
                Unique Skill identifier.

            skill_instance:
                Object implementing SkillInterface.

            version:
                Skill version.

            description:
                Skill description.
        """

        if self.registry.exists(skill_name):
            raise ValueError(
                f"Skill '{skill_name}' already installed."
            )

        self.registry.register(
            skill_name,
            version,
            description
        )

        self.loaded_skills[skill_name] = skill_instance

    def initialize_skill(
        self,
        skill_name: str
    ):
        """
        Initialize a Skill.
        """

        skill = self._get_skill(skill_name)

        skill.initialize()

        self.registry.update_status(
            skill_name,
            "initialized"
        )

    def activate_skill(
        self,
        skill_name: str
    ):
        """
        Activate a Skill.
        """

        skill = self._get_skill(skill_name)

        skill.activate()

        self.registry.update_status(
            skill_name,
            "active"
        )

    def deactivate_skill(
        self,
        skill_name: str
    ):
        """
        Deactivate a Skill.
        """

        skill = self._get_skill(skill_name)

        skill.deactivate()

        self.registry.update_status(
            skill_name,
            "inactive"
        )

    def process_event(
        self,
        skill_name: str,
        event: dict
    ):
        """
        Send an event to a Skill.
        """

        skill = self._get_skill(skill_name)

        skill.process_event(event)

    def get_skill_status(
        self,
        skill_name: str
    ):
        """
        Return Skill information.
        """

        return self.registry.get(skill_name)

    def list_skills(self):
        """
        Return all installed Skills.
        """

        return self.registry.list_all()

    def _get_skill(
        self,
        skill_name: str
    ):
        """
        Internal Skill retrieval.
        """

        if skill_name not in self.loaded_skills:
            raise ValueError(
                f"Skill '{skill_name}' is not loaded."
            )

        return self.loaded_skills[skill_name]