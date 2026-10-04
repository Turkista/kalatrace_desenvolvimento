"""Prediction: probabilistic projection of observable knowledge trends."""
from __future__ import annotations
import hashlib
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from graph.knowledge_graph import KnowledgeGraph
from horse.models import HorseExploration
from parsi.models import PARSIResult
from starhouse.models import StarHouseMap
from prediction.models import PredictionResult, PredictionScenario, PredictionSignal

class PredictionEngine:
    """Project plausible scenarios from existing structural signals.

    Prediction is deliberately non-generative with respect to knowledge: it
    does not create IECs, alter the graph, validate evidence, or claim truth.
    """
    VERSION = "1.0.0"

    def __init__(self, graph: Optional[KnowledgeGraph] = None) -> None:
        self.graph = graph or KnowledgeGraph()
        self._predictions = 0

    def predict(
        self,
        target_id: Optional[str] = None,
        statement: Optional[str] = None,
        horse_exploration: Optional[HorseExploration] = None,
        starhouse_map: Optional[StarHouseMap] = None,
        parsi_result: Optional[PARSIResult] = None,
        horizon: str = "medium_term",
        max_scenarios: int = 3,
    ) -> PredictionResult:
        if max_scenarios < 1:
            raise ValueError("max_scenarios must be >= 1")
        target = self._resolve_target(target_id, statement, parsi_result)
        signals = self._collect_signals(target, horse_exploration, starhouse_map)
        scenarios = self._build_scenarios(target, signals, horizon, max_scenarios)
        self._predictions += 1
        return PredictionResult(
            prediction_id=f"prediction:{self._predictions}",
            target_id=target or "",
            signals=signals,
            scenarios=scenarios,
            warnings=[
                "Predictions are probabilistic scenarios, not scientific conclusions.",
                "No experimental validation or causal inference was performed.",
                "Probability values are model scores under stated assumptions, not calibrated real-world probabilities.",
            ],
            provenance={
                "module": "Prediction", "version": self.VERSION,
                "inputs": {
                    "target_id": target_id, "statement_provided": bool(statement),
                    "parsi_used": parsi_result is not None,
                    "starhouse_used": starhouse_map is not None,
                    "horse_used": horse_exploration is not None,
                },
                "graph_mutated": False,
                "scientific_validation": "not_performed",
            },
        )

    def health_check(self) -> Dict[str, Any]:
        return {"module":"Prediction","version":self.VERSION,"status":"healthy","mutates_knowledge":False,"validates_truth":False}

    def stats(self) -> Dict[str, Any]:
        return {"version":self.VERSION,"predictions":self._predictions,"graph":self.graph.stats()}

    def _resolve_target(self, target_id: Optional[str], statement: Optional[str], result: Optional[PARSIResult]) -> Optional[str]:
        if target_id and target_id in self.graph.nodes:
            return target_id
        terms = []
        if result:
            terms.extend(e.normalized for e in result.entities if e.normalized)
        if statement:
            terms.extend(re.findall(r"[\wÀ-ÿ]+", statement.lower()))
        terms = list(dict.fromkeys(t.lower() for t in terms if t and len(t) > 2))
        for node_id, node in self.graph.nodes.items():
            text = " ".join(str(x or "") for x in (node_id, getattr(node,"label",None), getattr(node,"content",None), getattr(node,"statement",None))).lower()
            if any(t in text for t in terms):
                return node_id
        return target_id if target_id else None

    def _collect_signals(self, target: Optional[str], horse: Optional[HorseExploration], starhouse: Optional[StarHouseMap]) -> List[PredictionSignal]:
        signals: List[PredictionSignal] = []
        if target and target in self.graph.nodes:
            edges = self.graph.edges_of(target)
            if edges:
                conf = sum(float(e.get("confidence", 0.0)) for e in edges) / len(edges)
                signals.append(PredictionSignal(
                    signal_id=self._sid("connectivity", [target]), source_ids=[target],
                    signal_type="connectivity", strength=round(min(1.0, len(edges)/5.0), 6), direction="increasing",
                    explanation=f"Target has {len(edges)} observed graph connections with mean confidence {conf:.3f}.",
                    provenance={"module":"Prediction","validated":False},
                ))
        if horse and horse.paths:
            diverse = [p for p in horse.paths if len(p.node_ids) > 1]
            strength = min(1.0, len(diverse)/8.0)
            direction = "expanding" if strength >= .5 else "stable"
            signals.append(PredictionSignal(
                signal_id=self._sid("exploration", [p.path_id for p in diverse]),
                source_ids=[p.path_id for p in diverse], signal_type="exploration_frontier",
                strength=round(strength,6), direction=direction,
                explanation=f"Horse exposed {len(diverse)} candidate paths for forward scenario analysis.",
                provenance={"module":"Prediction","horse_validated":False},
            ))
        if starhouse:
            region_count = len(starhouse.regions)
            gaps = len(starhouse.gaps)
            strength = min(1.0, (region_count + gaps) / 10.0)
            direction = "emerging" if gaps > 0 else "stable"
            signals.append(PredictionSignal(
                signal_id=self._sid("landscape", [str(region_count), str(gaps)]),
                source_ids=[], signal_type="knowledge_landscape", strength=round(strength,6), direction=direction,
                explanation=f"Observed landscape contains {region_count} regions and {gaps} structural gaps.",
                provenance={"module":"Prediction","starhouse_validated":False},
            ))
        return signals

    def _build_scenarios(self, target: Optional[str], signals: Sequence[PredictionSignal], horizon: str, limit: int) -> List[PredictionScenario]:
        if not signals:
            return [PredictionScenario(
                scenario_id=self._sid("scenario", [target or "unknown"]),
                title="Insufficient structural signal", probability=0.34, horizon=horizon,
                assumptions=["Existing graph contains insufficient observable signals."], uncertainty=0.66,
                explanation="A defensible directional projection cannot be supported from the available structure.",
                provenance={"module":"Prediction","calibrated":False},
            )][:limit]
        mean = sum(s.strength for s in signals) / len(signals)
        expansion = sum(s.strength for s in signals if s.direction in {"increasing","expanding","emerging"}) / len(signals)
        stability = sum(s.strength for s in signals if s.direction == "stable") / len(signals)
        raw = [max(.05, expansion), max(.05, stability), max(.05, 1.0-mean)]
        total = sum(raw); probs = [round(x/total, 6) for x in raw]
        labels = [
            ("Expansion of the observed trajectory", "Structural signals continue to expand around the target."),
            ("Persistence of the current trajectory", "Observed structure remains broadly stable over the selected horizon."),
            ("Weakening or divergence", "Current signals become less coherent or fail to extend into new structure."),
        ]
        scenarios=[]
        for i,(prob,(title,explanation)) in enumerate(zip(probs,labels)):
            scenarios.append(PredictionScenario(
                scenario_id=self._sid("scenario", [target or "unknown", str(i)]), title=title,
                probability=prob, horizon=horizon, supporting_signals=[s.signal_id for s in signals],
                assumptions=["Projection is based only on observed graph/cartography signals.", "No causal mechanism was established."],
                uncertainty=round(max(.0, 1.0-prob),6), explanation=explanation,
                provenance={"module":"Prediction","calibrated":False,"scientific_validation":"not_performed"},
            ))
        return sorted(scenarios, key=lambda s: -s.probability)[:limit]

    @staticmethod
    def _sid(prefix: str, values: Iterable[str]) -> str:
        return f"prediction:{prefix}:" + hashlib.sha1("|".join(values).encode()).hexdigest()[:12]

Prediction = PredictionEngine
