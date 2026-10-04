"""
KALATRACE Core Registry

Public registry components used for
component discovery, registration and
lifecycle management.
"""

from .registry_entry import (
    ComponentType,
    RegistryEntry,
)

from .registry import (
    Registry,
)

from .registry_manager import (
    RegistryManager,
)


__all__ = [
    # Component Definition
    "RegistryEntry",
    "ComponentType",

    # Storage
    "Registry",

    # Coordination
    "RegistryManager",
]