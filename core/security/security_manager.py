"""
KALATRACE Security Manager

Controls permissions and trust relationships
between components.

Migrated from kernel/security/security_manager.py
as part of ADR-001 (T1.1c) — no prior equivalent
in core/.
"""

from typing import Dict, Set


class SecurityManager:
    """
    Central Kernel security service.
    """

    def __init__(
        self
    ):
        """
        Initializes security manager.
        """

        self.trusted_modules: Set[str] = set()

        self.permissions: Dict[
            str,
            Set[str]
        ] = {}

    # =================================================
    # Trusted Modules
    # =================================================

    def register_module(
        self,
        module_name: str
    ):
        """
        Registers a trusted module.
        """

        self.trusted_modules.add(
            module_name
        )

    def unregister_module(
        self,
        module_name: str
    ):
        """
        Removes a trusted module.
        """

        self.trusted_modules.discard(
            module_name
        )

    def is_trusted(
        self,
        module_name: str
    ) -> bool:
        """
        Checks whether a module is trusted.
        """

        return (
            module_name
            in
            self.trusted_modules
        )

    # =================================================
    # Permissions
    # =================================================

    def grant_permission(
        self,
        module_name: str,
        permission: str
    ):
        """
        Grants a permission.
        """

        self.permissions.setdefault(
            module_name,
            set()
        ).add(permission)

    def revoke_permission(
        self,
        module_name: str,
        permission: str
    ):
        """
        Removes a permission.
        """

        if module_name in self.permissions:

            self.permissions[
                module_name
            ].discard(permission)

    def has_permission(
        self,
        module_name: str,
        permission: str
    ) -> bool:
        """
        Checks whether a permission exists.
        """

        return (
            permission
            in
            self.permissions.get(
                module_name,
                set()
            )
        )

    def list_permissions(
        self,
        module_name: str
    ) -> list[str]:
        """
        Returns module permissions.
        """

        return sorted(
            self.permissions.get(
                module_name,
                set()
            )
        )

    # =================================================
    # Maintenance
    # =================================================

    def clear(
        self
    ):
        """
        Removes every registration.
        """

        self.permissions.clear()

        self.trusted_modules.clear()

    # =================================================
    # Information
    # =================================================

    def __repr__(
        self
    ):
        return (
            f"<SecurityManager "
            f"trusted_modules={len(self.trusted_modules)} "
            f"permissions={len(self.permissions)}>"
        )