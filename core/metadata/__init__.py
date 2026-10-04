"""
KALATRACE Core Metadata

Public metadata package.

This package exposes the metadata objects shared across
the KALATRACE architecture, including the Registry,
Runtime, Component Loader, Discovery and Orchestrator.
"""

from .metadata import Metadata
from .version import Version
from .capability import Capability, CapabilityType
from .dependency import Dependency, DependencyType
from .component_metadata import ComponentMetadata


__all__ = [
    "Metadata",
    "Version",
    "Capability",
    "CapabilityType",
    "Dependency",
    "DependencyType",
    "ComponentMetadata",
]