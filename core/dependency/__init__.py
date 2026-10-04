"""
KALATRACE Core Dependency

Public interface for dependency injection:
container, registry, locator and injector.
"""

from .dependency_container import (
    DependencyContainer,
)

from .service_registry import (
    ServiceRegistry,
)

from .service_locator import (
    ServiceLocator,
)

from .injector import (
    Injector,
)


__all__ = [
    "DependencyContainer",
    "ServiceRegistry",
    "ServiceLocator",
    "Injector",
]
