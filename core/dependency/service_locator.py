"""
KALATRACE Service Locator

Provides centralized access to Kernel services.

The Service Locator does not create services.
It only retrieves services registered
inside the Service Registry.

Migrated from kernel/dependency/service_locator.py
as part of ADR-001 (T1.1b) — no prior equivalent in core/.
"""


class ServiceLocator:
    """
    Global access point for Kernel services.
    """

    _registry = None


    @classmethod
    def configure(cls, registry):
        """
        Connects the locator to a Service Registry.

        Args:
            registry:
                ServiceRegistry instance.
        """

        cls._registry = registry


    @classmethod
    def get(cls, name):
        """
        Retrieves a service by name.
        """

        if cls._registry is None:
            raise RuntimeError(
                "Service Locator not configured."
            )

        return cls._registry.get(name)


    @classmethod
    def exists(cls, name):
        """
        Checks if a service exists.
        """

        if cls._registry is None:
            return False

        return cls._registry.exists(name)


    @classmethod
    def clear(cls):
        """
        Removes registry reference.
        """

        cls._registry = None