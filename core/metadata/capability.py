"""
KALATRACE Core

Capability Metadata

Defines immutable metadata describing the capabilities exposed by
system components. Capabilities are used by the Registry, Runtime,
Discovery, ServiceContainer and Orchestrator to identify, discover
and resolve component functionality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum



class CapabilityType(Enum):
    """
    High-level categories of component capabilities.
    """

    COMPUTATION = "computation"
    ANALYSIS = "analysis"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    REASONING = "reasoning"
    PERCEPTION = "perception"
    CONTROL = "control"
    CUSTOM = "custom"

    VALIDATION = "validation"
    DISCOVERY = "discovery"
    INFERENCE = "inference"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    MONITORING = "monitoring"
    KNOWLEDGE = "knowledge"
    WORKFLOW = "workflow"
    SIMULATION = "simulation"


@dataclass(frozen=True, slots=True)
class Capability:
    """
    Immutable description of a capability exposed by a component.

    A capability represents a specific functionality that can be
    advertised, discovered and consumed by other parts of the
    KALATRACE ecosystem.

    This metadata supports:

    - Component discovery
    - Dynamic service resolution
    - Runtime inspection
    - Registry indexing
    - Capability-based orchestration
    """

    identifier: str

    name: str

    capability_type: CapabilityType

    description: str = ""

    version: str = "1.0.0"

    tags: tuple[str, ...] = field(
        default_factory=tuple
    )


    def __post_init__(self) -> None:
        """
        Validate and normalize capability metadata.
        """

        identifier = self.identifier.strip()

        name = self.name.strip()

        description = self.description.strip()

        version = self.version.strip()


        if not identifier:
            raise ValueError(
                "Capability identifier cannot be empty."
            )

        if not name:
            raise ValueError(
                "Capability name cannot be empty."
            )

        if not version:
            raise ValueError(
                "Capability version cannot be empty."
            )


        normalized_tags = tuple(
            tag.strip()
            for tag in self.tags
            if tag.strip()
        )


        object.__setattr__(
            self,
            "identifier",
            identifier,
        )

        object.__setattr__(
            self,
            "name",
            name,
        )

        object.__setattr__(
            self,
            "description",
            description,
        )

        object.__setattr__(
            self,
            "version",
            version,
        )

        object.__setattr__(
            self,
            "tags",
            normalized_tags,
        )