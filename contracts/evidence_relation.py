from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict

EPISTEMIC_RELATIONS = ("SUPPORTS", "CONTRADICTS", "NEUTRAL")


@dataclass
class EvidenceRelation:
    """Relação epistemológica de uma evidência diante de uma IEC."""

    id: str
    evidence_id: str
    iec_id: str
    relation: str = "SUPPORTS"
    weight: float = 1.0
    reason: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    validated_at: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def relation_id(self) -> str:
        return self.id

    def validate(self) -> None:
        if not self.id or not self.evidence_id or not self.iec_id:
            raise ValueError("EvidenceRelation precisa de id, evidence_id e iec_id")
        if self.relation not in EPISTEMIC_RELATIONS:
            raise ValueError(f"Relação epistemológica inválida: {self.relation}")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("weight deve estar entre 0 e 1")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "iec_id": self.iec_id,
            "relation": self.relation,
            "weight": self.weight,
            "reason": self.reason,
            "created_at": self.created_at,
            "validated_at": self.validated_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "EvidenceRelation":
        relation = cls(
            id=payload.get("id", payload.get("relation_id", "")),
            evidence_id=payload.get("evidence_id", ""),
            iec_id=payload.get("iec_id", ""),
            relation=payload.get("relation", "SUPPORTS"),
            weight=float(payload.get("weight", 1.0)),
            reason=payload.get("reason", ""),
            created_at=payload.get("created_at", datetime.now(UTC).isoformat()),
            validated_at=payload.get("validated_at"),
            metadata=dict(payload.get("metadata", {})),
        )
        relation.validate()
        return relation
