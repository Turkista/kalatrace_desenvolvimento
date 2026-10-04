"""Data contracts for the KALATRACE probabilistic prediction layer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

@dataclass(frozen=True)
class PredictionSignal:
    signal_id: str
    source_ids: List[str] = field(default_factory=list)
    signal_type: str = "structural_trend"
    strength: float = 0.0
    direction: str = "stable"
    explanation: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class PredictionScenario:
    scenario_id: str
    title: str
    probability: float
    horizon: str = "unspecified"
    supporting_signals: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    uncertainty: float = 1.0
    explanation: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class PredictionResult:
    prediction_id: str
    target_id: str = ""
    signals: List[PredictionSignal] = field(default_factory=list)
    scenarios: List[PredictionScenario] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "signals": [s.to_dict() for s in self.signals],
            "scenarios": [s.to_dict() for s in self.scenarios],
        }
