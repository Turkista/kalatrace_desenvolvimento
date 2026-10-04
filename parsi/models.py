"""Data contracts for the PARSI cognitive interpretation layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SemanticEntity:
    """Candidate entity extracted from an input without asserting truth."""

    text: str
    normalized: str
    entity_type: str = "concept"
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticRelation:
    """Candidate relation expressed by the source text."""

    source: str
    relation: str
    target: str
    cue: str
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticContext:
    """Contextual signals extracted from the input text."""

    language: str
    modality: str
    polarity: str
    temporal_markers: List[str] = field(default_factory=list)
    domain_hints: List[str] = field(default_factory=list)
    source_hints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PARSIResult:
    """Complete interpretation produced by PARSI.

    `interpretation_confidence` measures confidence in the structural
    interpretation only. It is deliberately not an epistemic/scientific
    truth score.
    """

    interpretation_id: str
    raw_text: str
    normalized_text: str
    intent: str
    summary: str
    entities: List[SemanticEntity]
    relations: List[SemanticRelation]
    context: SemanticContext
    interpretation_confidence: float
    warnings: List[str] = field(default_factory=list)
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["entities"] = [item.to_dict() for item in self.entities]
        data["relations"] = [item.to_dict() for item in self.relations]
        data["context"] = self.context.to_dict()
        return data

    @property
    def primary_entity(self) -> Optional[str]:
        return self.entities[0].normalized if self.entities else None
