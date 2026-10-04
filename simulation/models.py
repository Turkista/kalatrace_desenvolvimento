"""Contracts for the KALATRACE virtual experimentation layer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

@dataclass(frozen=True)
class SimulationChange:
    field: str
    value: Any
    rationale: str = ""
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class SimulationOutcome:
    outcome_id: str
    label: str
    score: float
    observations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    uncertainty: float = 1.0
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class SimulationScenario:
    scenario_id: str
    title: str
    baseline_id: str = ""
    changes: List[SimulationChange] = field(default_factory=list)
    outcomes: List[SimulationOutcome] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return {**asdict(self), "changes":[c.to_dict() for c in self.changes], "outcomes":[o.to_dict() for o in self.outcomes]}

@dataclass(frozen=True)
class SimulationResult:
    simulation_id: str
    scenarios: List[SimulationScenario] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return {**asdict(self), "scenarios":[s.to_dict() for s in self.scenarios]}
