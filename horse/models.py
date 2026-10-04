"""Contracts for the Horse non-linear cognitive exploration module."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

@dataclass(frozen=True)
class HorsePath:
    path_id: str
    node_ids: List[str] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)
    score: float = 0.0
    rationale: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class HorseExploration:
    exploration_id: str
    seed_ids: List[str] = field(default_factory=list)
    paths: List[HorsePath] = field(default_factory=list)
    frontier_node_ids: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["paths"] = [p.to_dict() for p in self.paths]
        return data
