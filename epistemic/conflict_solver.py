"""Deterministic epistemic conflict resolution for KALATRACE.

This module resolves an already detected conflict. It does not persist state,
mutate IECs, or decide scientific truth. Persistence and lifecycle effects
remain responsibilities of the Knowledge Evolution Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


SUPPORTS = "SUPPORTS"
CONTRADICTS = "CONTRADICTS"
NEUTRAL = "NEUTRAL"

DECISION_SUPPORTS = SUPPORTS
DECISION_CONTRADICTS = CONTRADICTS
DECISION_UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ConflictDecision:
    """Pure result of resolving competing evidence."""

    decision: str
    support_score: float
    contradiction_score: float
    margin: float
    evidence_count: int
    rationale: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def resolved(self) -> bool:
        return self.decision != DECISION_UNRESOLVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "support_score": self.support_score,
            "contradiction_score": self.contradiction_score,
            "margin": self.margin,
            "evidence_count": self.evidence_count,
            "rationale": self.rationale,
            "evidence_ids": list(self.evidence_ids),
            "resolved": self.resolved,
        }


class ConflictSolver:
    """Resolve evidence conflicts without mutating epistemic state.

    Effective evidence strength is weight multiplied by reliability when
    reliability is supplied, otherwise weight. A deterministic margin
    threshold avoids silently selecting a side when evidence is effectively tied.
    """

    VALID_RELATIONS = {SUPPORTS, CONTRADICTS, NEUTRAL}

    def __init__(self, *, minimum_margin: float = 0.05) -> None:
        if minimum_margin < 0:
            raise ValueError("minimum_margin must be non-negative.")
        self.minimum_margin = float(minimum_margin)

    @classmethod
    def _normalize_relation(cls, relation: Any) -> str:
        normalized = str(relation or "").strip().upper()
        if normalized not in cls.VALID_RELATIONS:
            raise ValueError(
                f"Unsupported evidence relation: {relation!r}. "
                f"Expected one of {sorted(cls.VALID_RELATIONS)}."
            )
        return normalized

    @staticmethod
    def _strength(link: Mapping[str, Any]) -> float:
        try:
            weight = float(link.get("weight", 1.0))
            reliability = float(link.get("reliability", 1.0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Evidence weight/reliability must be numeric.") from exc

        if weight < 0 or reliability < 0:
            raise ValueError("Evidence weight/reliability cannot be negative.")

        return weight * reliability

    def resolve(self, links: Iterable[Mapping[str, Any]]) -> ConflictDecision:
        """Resolve a collection of evidence-to-IEC relation records."""

        support_score = 0.0
        contradiction_score = 0.0
        evidence_ids: list[str] = []
        count = 0

        for link in links:
            relation = self._normalize_relation(link.get("relation"))
            strength = self._strength(link)
            count += 1

            evidence_id = link.get("evidence_id")
            if evidence_id is not None:
                evidence_ids.append(str(evidence_id))

            if relation == SUPPORTS:
                support_score += strength
            elif relation == CONTRADICTS:
                contradiction_score += strength

        margin = abs(support_score - contradiction_score)

        if support_score == 0 and contradiction_score == 0:
            decision = DECISION_UNRESOLVED
            rationale = "No weighted support or contradiction evidence is available."
        elif margin < self.minimum_margin:
            decision = DECISION_UNRESOLVED
            rationale = (
                "Support and contradiction evidence are too closely balanced "
                "to resolve deterministically."
            )
        elif support_score > contradiction_score:
            decision = DECISION_SUPPORTS
            rationale = (
                "Weighted supporting evidence exceeds weighted contradictory evidence."
            )
        else:
            decision = DECISION_CONTRADICTS
            rationale = (
                "Weighted contradictory evidence exceeds weighted supporting evidence."
            )

        return ConflictDecision(
            decision=decision,
            support_score=support_score,
            contradiction_score=contradiction_score,
            margin=margin,
            evidence_count=count,
            rationale=rationale,
            evidence_ids=tuple(evidence_ids),
        )
