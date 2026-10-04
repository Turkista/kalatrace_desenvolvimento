"""Simulation: isolated virtual experimentation without mutation of official knowledge."""
from __future__ import annotations
import hashlib
from typing import Any, Dict, Iterable, List, Optional, Sequence
from graph.knowledge_graph import KnowledgeGraph
from prediction.models import PredictionResult
from horse.models import HorseExploration
from starhouse.models import StarHouseMap
from simulation.models import SimulationChange, SimulationOutcome, SimulationScenario, SimulationResult

class SimulationEngine:
    VERSION = "1.0.0"

    def __init__(self, graph: Optional[KnowledgeGraph] = None) -> None:
        self.graph = graph or KnowledgeGraph()
        self._simulations = 0

    def simulate(
        self,
        title: str = "Virtual experiment",
        changes: Optional[Sequence[SimulationChange | Dict[str, Any]]] = None,
        prediction: Optional[PredictionResult] = None,
        horse_exploration: Optional[HorseExploration] = None,
        starhouse_map: Optional[StarHouseMap] = None,
        baseline_id: str = "current_knowledge",
        alternatives: int = 3,
    ) -> SimulationResult:
        if alternatives < 1:
            raise ValueError("alternatives must be >= 1")
        normalized = self._normalize_changes(changes or [])
        base = self._baseline_signal(prediction, horse_exploration, starhouse_map)
        scenarios = self._build_scenarios(title, normalized, base, prediction, alternatives, baseline_id)
        self._simulations += 1
        return SimulationResult(
            simulation_id=f"simulation:{self._simulations}", scenarios=scenarios,
            warnings=[
                "Simulation operates on hypothetical state only.",
                "No official KnowledgeGraph state was mutated.",
                "Simulation outcomes are model outputs, not validated predictions or causal conclusions.",
                "Results must not be incorporated into official knowledge without the appropriate epistemic process.",
            ],
            provenance={"module":"Simulation","version":self.VERSION,"graph_mutated":False,"scientific_validation":"not_performed"},
        )

    def health_check(self) -> Dict[str, Any]:
        return {"module":"Simulation","version":self.VERSION,"status":"healthy","mutates_knowledge":False,"validates_truth":False}

    def stats(self) -> Dict[str, Any]:
        return {"version":self.VERSION,"simulations":self._simulations,"graph":self.graph.stats()}

    @staticmethod
    def _normalize_changes(changes: Sequence[SimulationChange | Dict[str, Any]]) -> List[SimulationChange]:
        result=[]
        for item in changes:
            if isinstance(item, SimulationChange): result.append(item)
            elif isinstance(item, dict): result.append(SimulationChange(field=str(item.get("field","unknown")), value=item.get("value"), rationale=str(item.get("rationale",""))))
            else: raise TypeError("changes must contain SimulationChange or dict values")
        return result

    @staticmethod
    def _baseline_signal(prediction, horse, starhouse) -> float:
        values=[]
        if prediction and prediction.scenarios: values.append(max(s.probability for s in prediction.scenarios))
        if horse and horse.paths: values.append(min(1.0, len(horse.paths)/8.0))
        if starhouse: values.append(min(1.0, (len(starhouse.regions)+len(starhouse.gaps))/10.0))
        return sum(values)/len(values) if values else .5

    def _build_scenarios(self, title, changes, base, prediction, alternatives, baseline_id):
        change_factor = min(.35, .05 * len(changes))
        labels=[("Conservative response", .55), ("Amplified response", .75), ("Divergent response", .35)]
        scenarios=[]
        for idx,(label,mult) in enumerate(labels[:alternatives]):
            score=max(0.0,min(1.0,base*mult + change_factor))
            outcome=SimulationOutcome(
                outcome_id=self._sid("outcome",[title,str(idx)]), label=label, score=round(score,6),
                observations=[f"Virtual response score derived from baseline signal {base:.3f}.", f"Applied {len(changes)} hypothetical change(s)."],
                assumptions=["Scenario is hypothetical.", "Model does not establish causality.", "Existing graph remains unchanged."],
                uncertainty=round(1.0-score*.6,6),
                provenance={"module":"Simulation","calibrated":False,"validated":False},
            )
            scenarios.append(SimulationScenario(
                scenario_id=self._sid("scenario",[title,str(idx)]), title=f"{title} — {label}", baseline_id=baseline_id,
                changes=changes, outcomes=[outcome],
                warnings=["Outcome is hypothetical and must not be interpreted as an observed fact."],
                provenance={"module":"Simulation","prediction_used":prediction is not None,"graph_mutated":False},
            ))
        return scenarios

    @staticmethod
    def _sid(prefix: str, values: Iterable[str]) -> str:
        return f"simulation:{prefix}:" + hashlib.sha1("|".join(values).encode()).hexdigest()[:12]

Simulation = SimulationEngine
