"""
KALATRACE Dependency Injector

Responsible for injecting registered services
into components that require them.

Migrated from kernel/dependency/injector.py as
part of ADR-001 (T1.1b) — no prior equivalent in core/.
"""

import inspect


class Injector:
    """
    Dependency injection manager.
    """


    def __init__(self, registry):
        """
        Args:
            registry:
                ServiceRegistry instance.
        """

        self.registry = registry


    def resolve(self, cls):
        """
        Creates an instance of a class
        injecting required dependencies.
        """

        signature = inspect.signature(
            cls.__init__
        )

        dependencies = {}


        for name, parameter in signature.parameters.items():

            if name == "self":
                continue


            if self.registry.exists(name):

                dependencies[name] = (
                    self.registry.get(name)
                )


        return cls(
            **dependencies
        )


    def inject(self, instance):
        """
        Injects dependencies into an
        existing instance.

        """

        attributes = (
            getattr(
                instance,
                "__dependencies__",
                []
            )
        )


        for dependency in attributes:

            if self.registry.exists(
                dependency
            ):

                setattr(
                    instance,
                    dependency,
                    self.registry.get(
                        dependency
                    )
                )


        return instance