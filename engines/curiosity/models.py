from dataclasses import dataclass, field
from typing import List


@dataclass
class KnowledgeGap:

    id: str

    description: str

    affected_nodes: List[str]

    confidence: float

    severity: float


@dataclass
class ResearchQuestion:

    id: str

    question: str

    rationale: str

    priority: float

    related_nodes: List[str]


@dataclass
class CuriosityReport:

    gaps: List[KnowledgeGap] = field(default_factory=list)

    questions: List[ResearchQuestion] = field(default_factory=list)

    contradictions: List[str] = field(default_factory=list)

    opportunities: List[str] = field(default_factory=list)