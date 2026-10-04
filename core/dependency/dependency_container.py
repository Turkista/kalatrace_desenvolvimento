"""
KALATRACE Dependency Container

Central dependency management container.

Migrated from kernel/dependency/dependency_container.py
as part of ADR-001 (T1.1b) — no prior equivalent in core/.
"""

from typing import Any


class DependencyContainer:
    """
    Stores and manages shared Kernel dependencies.
    """

    def __init__(
        self
    ):
        self._dependencies: dict[
            str,
            Any
        ] = {}

        self.initialized = False


    # =================================================
    # Lifecycle
    # =================================================

    def initialize(
        self
    ):
        """
        Initializes dependency container.
        """

        if self.initialized:
            return

        self.initialized = True


    def shutdown(
        self
    ):
        """
        Releases dependencies.
        """

        self.clear()

        self.initialized = False


    # =================================================
    # Registration
    # =================================================

    def register(
        self,
        name: str,
        dependency: Any
    ):
        """
        Registers a dependency.
        """

        self._ensure_initialized()

        if name in self._dependencies:

            raise ValueError(
                f"Dependency already registered: {name}"
            )

        self._dependencies[name] = dependency



    def replace(
        self,
        name: str,
        dependency: Any
    ):
        """
        Replaces a dependency.
        """

        self._ensure_initialized()

        self._dependencies[name] = dependency



    # =================================================
    # Resolution
    # =================================================

    def resolve(
        self,
        name: str
    ) -> Any:
        """
        Resolves dependency.
        """

        self._ensure_initialized()

        if name not in self._dependencies:

            raise KeyError(
                f"Dependency not found: {name}"
            )

        return self._dependencies[name]



    def exists(
        self,
        name: str
    ) -> bool:

        return (
            name in self._dependencies
        )



    # =================================================
    # Removal
    # =================================================

    def remove(
        self,
        name: str
    ):
        """
        Removes dependency.
        """

        self._dependencies.pop(
            name,
            None
        )


    def clear(
        self
    ):
        """
        Clears dependencies.
        """

        self._dependencies.clear()



    # =================================================
    # Information
    # =================================================

    def list_dependencies(
        self
    ) -> list[str]:

        return sorted(
            self._dependencies.keys()
        )


    def count(
        self
    ) -> int:

        return len(
            self._dependencies
        )



    # =================================================
    # Internal
    # =================================================

    def _ensure_initialized(
        self
    ):
        """
        Validates container state.
        """

        if not self.initialized:

            raise RuntimeError(
                "Dependency Container not initialized."
            )


    # =================================================
    # Representation
    # =================================================

    def __repr__(
        self
    ):

        return (
            f"<DependencyContainer "
            f"dependencies={len(self._dependencies)}>"
        )