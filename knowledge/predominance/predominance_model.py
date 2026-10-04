"""
Predominance Model

Defines the data structure responsible for representing
the predominance state of a knowledge entity.

A PredominanceModel does not represent truth.
It represents the current relative strength of a
knowledge hypothesis based on available evidence,
relationships, evolution and contradictions.
"""


from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Dict


@dataclass
class PredominanceModel:
    """
    Represents the predominance profile of a knowledge entity.

    Attributes:
        entity_id:
            Identifier of the analyzed knowledge entity.

        score:
            Numerical predominance score between 0 and 1.

        classification:
            Current predominance classification.

        evidence_strength:
            Strength derived from available evidence.

        replication_score:
            Degree of replication across studies.

        methodological_quality:
            Quality of methodologies supporting the knowledge.

        network_influence:
            Influence of the entity inside the knowledge graph.

        temporal_relevance:
            Current scientific relevance over time.

        contradiction_penalty:
            Reduction factor caused by contradictory evidence.

        supporting_factors:
            Reasons increasing predominance.

        limiting_factors:
            Factors reducing confidence.

        created_at:
            Timestamp of analysis creation.
    """

    entity_id: str

    score: float = 0.0

    classification: str = "UNKNOWN"

    evidence_strength: float = 0.0

    replication_score: float = 0.0

    methodological_quality: float = 0.0

    network_influence: float = 0.0

    temporal_relevance: float = 0.0

    contradiction_penalty: float = 0.0

    supporting_factors: List[str] = field(
        default_factory=list
    )

    limiting_factors: List[str] = field(
        default_factory=list
    )

    metadata: Dict = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


    def update_classification(self):
        """
        Updates the qualitative classification
        according to the numerical score.
        """

        if self.score < 0.25:
            self.classification = "DORMANT"

        elif self.score < 0.50:
            self.classification = "EMERGING"

        elif self.score < 0.75:
            self.classification = "SUPPORTED"

        elif self.score < 0.90:
            self.classification = "DOMINANT"

        else:
            self.classification = "STRONG_CONSENSUS"


    def add_supporting_factor(
        self,
        factor: str
    ):
        """
        Adds a positive factor influencing predominance.
        """

        self.supporting_factors.append(
            factor
        )


    def add_limiting_factor(
        self,
        factor: str
    ):
        """
        Adds a limiting factor.
        """

        self.limiting_factors.append(
            factor
        )


    def to_dict(self) -> Dict:
        """
        Converts the model into a serializable structure.
        """

        return {
            "entity_id": self.entity_id,
            "score": self.score,
            "classification": self.classification,

            "evidence_strength":
                self.evidence_strength,

            "replication_score":
                self.replication_score,

            "methodological_quality":
                self.methodological_quality,

            "network_influence":
                self.network_influence,

            "temporal_relevance":
                self.temporal_relevance,

            "contradiction_penalty":
                self.contradiction_penalty,

            "supporting_factors":
                self.supporting_factors,

            "limiting_factors":
                self.limiting_factors,

            "metadata":
                self.metadata,

            "created_at":
                self.created_at.isoformat()
        }