"""Data contracts for the StarHouse cognitive observatory."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class KnowledgeRegion:
    """A cartographic region grouped by a stable knowledge domain."""

    region_id: str
    label: str
    node_ids: List[str] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "label": self.label,
            "node_ids": list(self.node_ids),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "density": self.density,
        }


@dataclass(frozen=True)
class KnowledgeConnection:
    """Observed connection between two knowledge nodes."""

    source_id: str
    target_id: str
    relation_type: str
    confidence: float
    weight: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class KnowledgeGap:
    """A structural gap observed in the current knowledge map."""

    gap_type: str
    node_ids: List[str]
    severity: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_type": self.gap_type,
            "node_ids": list(self.node_ids),
            "severity": self.severity,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class StarHouseMap:
    """Immutable observation of the knowledge universe at one point in time."""

    version: str
    node_count: int
    edge_count: int
    regions: List[KnowledgeRegion]
    connections: List[KnowledgeConnection]
    gaps: List[KnowledgeGap]
    isolated_node_ids: List[str]
    low_confidence_edge_count: int
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "regions": [item.to_dict() for item in self.regions],
            "connections": [item.to_dict() for item in self.connections],
            "gaps": [item.to_dict() for item in self.gaps],
            "isolated_node_ids": list(self.isolated_node_ids),
            "low_confidence_edge_count": self.low_confidence_edge_count,
            "provenance": dict(self.provenance),
        }
