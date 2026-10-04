from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import (
    CuriosityReport,
    ResearchQuestion,
)


class GapDetector(ABC):

    @abstractmethod
    def detect(self) -> CuriosityReport:
        pass


class ContradictionDetector(ABC):

    @abstractmethod
    def detect(self) -> CuriosityReport:
        pass


class OpportunityDetector(ABC):

    @abstractmethod
    def detect(self) -> CuriosityReport:
        pass


class QuestionGenerator(ABC):

    @abstractmethod
    def generate(self) -> List[ResearchQuestion]:
        pass


class PriorityRanker(ABC):

    @abstractmethod
    def rank(
        self,
        questions: List[ResearchQuestion]
    ) -> List[ResearchQuestion]:
        pass