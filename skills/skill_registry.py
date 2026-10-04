"""
KALATRACE Skill Registry

Manages the registration and metadata of all installed KALATRACE Skills.

The registry does not execute Skills.
It only maintains information about available modules.
"""

from datetime import datetime, UTC


class SkillRegistry:
    """
    Central registry for KALATRACE Skills.
    """

    def __init__(self):
        self.skills = {}

    def register(
        self,
        skill_name: str,
        version: str,
        description: str = ""
    ):
        """
        Register a new Skill.

        Args:
            skill_name:
                Unique identifier of the Skill.

            version:
                Current Skill version.

            description:
                Short description of the Skill purpose.
        """

        if skill_name in self.skills:
            raise ValueError(
                f"Skill '{skill_name}' is already registered."
            )

        self.skills[skill_name] = {
            "name": skill_name,
            "version": version,
            "description": description,
            "status": "registered",
            "registered_at": datetime.now(UTC)
        }

    def unregister(self, skill_name: str):
        """
        Remove a Skill from registry.
        """

        if skill_name not in self.skills:
            raise ValueError(
                f"Skill '{skill_name}' was not found."
            )

        del self.skills[skill_name]

    def exists(self, skill_name: str) -> bool:
        """
        Check if a Skill exists.
        """

        return skill_name in self.skills

    def get(self, skill_name: str):
        """
        Retrieve Skill information.
        """

        return self.skills.get(skill_name)

    def update_status(
        self,
        skill_name: str,
        status: str
    ):
        """
        Update Skill lifecycle status.

        Examples:
            registered
            initialized
            active
            inactive
            error
        """

        if skill_name not in self.skills:
            raise ValueError(
                f"Skill '{skill_name}' was not found."
            )

        self.skills[skill_name]["status"] = status

    def list_all(self):
        """
        Return all registered Skills.
        """

        return list(self.skills.values())
