"""
KALATRACE
Confidence Management System

Foundation Layer

Responsabilidade:
Controle epistemológico da confiança
das entidades do sistema.

Blueprint:
KALATRACE Blueprint 3.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared.enums import ConfidenceLevel


# ==========================================================
# Confidence Score
# ==========================================================


@dataclass(frozen=True)
class ConfidenceScore:
    """
    Representa a confiança epistemológica
    de uma entidade.

    O valor numérico é a única fonte
    de verdade.

    O nível (WEAK, STRONG, etc.)
    é calculado automaticamente
    pelo ConfidenceClassifier.

    Dessa forma eliminamos qualquer
    inconsistência entre valor e classificação.
    """

    value: float

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    def __post_init__(self):

        if not 0.0 <= self.value <= 1.0:

            raise ValueError(
                "Confidence deve estar entre 0.0 e 1.0."
            )

    @property
    def level(self) -> ConfidenceLevel:
        """
        Classificação automática da confiança.

        Nunca é armazenada.
        Sempre é derivada do valor.
        """

        return ConfidenceClassifier.classify(
            self.value
        )

    @property
    def percentage(self) -> float:
        """
        Retorna o valor percentual.
        """

        return self.value * 100

    @property
    def is_reliable(self) -> bool:
        """
        Indica se a confiança é considerada
        suficiente para utilização científica.
        """

        return ConfidenceClassifier.is_reliable(
            self.value
        )

    def to_dict(self):

        return {

            "value":
                self.value,

            "level":
                self.level.value,

            "percentage":
                self.percentage,

            "created_at":
                self.created_at.isoformat()

        }

    def __float__(self):

        return self.value

    def __str__(self):

        return (
            f"{self.value:.2f}"
            f" ({self.level.value})"
        )

    def __repr__(self):

        return (
            "ConfidenceScore("
            f"value={self.value:.2f}, "
            f"level={self.level.value})"
        )
# ==========================================================
# Confidence Classification
# ==========================================================


class ConfidenceClassifier:
    """
    Responsável pela interpretação epistemológica
    dos valores de confiança.

    Esta classe representa a única autoridade
    para classificar níveis de confiança
    dentro do KALATRACE.

    Nenhum outro módulo deve implementar
    regras próprias de classificação.
    """

    # ------------------------------------------------------
    # Classification
    # ------------------------------------------------------

    @staticmethod
    def classify(
        value: float
    ) -> ConfidenceLevel:
        """
        Classifica automaticamente
        um valor de confiança.

        Escala utilizada:

        0.00–0.19  WEAK

        0.20–0.49  MODERATE

        0.50–0.79  STRONG

        0.80–1.00  VERY_STRONG
        """

        if not 0.0 <= value <= 1.0:

            raise ValueError(
                "Confidence deve estar entre 0.0 e 1.0."
            )

        if value < 0.20:

            return ConfidenceLevel.WEAK

        if value < 0.50:

            return ConfidenceLevel.MODERATE

        if value < 0.80:

            return ConfidenceLevel.STRONG

        return ConfidenceLevel.VERY_STRONG

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    @staticmethod
    def is_reliable(
        value: float
    ) -> bool:
        """
        Determina se uma confiança
        é suficiente para utilização
        científica.

        O limiar atual é 0.50.

        Esse valor poderá ser ajustado
        futuramente pela camada
        de Governança.
        """

        return value >= 0.50

    # ------------------------------------------------------
    # Comparison
    # ------------------------------------------------------

    @staticmethod
    def compare(
        first: float,
        second: float
    ) -> int:
        """
        Compara dois valores.

        Retorna

        -1  menor

         0  igual

         1  maior
        """

        if first < second:

            return -1

        if first > second:

            return 1

        return 0

    # ------------------------------------------------------
    # Utilities
    # ------------------------------------------------------

    @staticmethod
    def normalize(
        value: float
    ) -> float:
        """
        Garante que o valor permaneça
        dentro do intervalo permitido.
        """

        return max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )
# ==========================================================
# Confidence Operations
# ==========================================================


class ConfidenceCalculator:
    """
    Responsável pelas operações matemáticas
    sobre confiança epistemológica.

    Nenhuma Engine deve implementar
    cálculos próprios de confiança.

    Toda evolução deve passar
    por esta classe.
    """

    # ------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------

    @staticmethod
    def average(
        scores: list[ConfidenceScore]
    ) -> float:
        """
        Calcula a média simples
        entre múltiplos ConfidenceScore.
        """

        if not scores:

            return 0.0

        return sum(

            score.value

            for score in scores

        ) / len(scores)

    @staticmethod
    def weighted_average(
        scores: list[
            tuple[
                ConfidenceScore,
                float
            ]
        ]
    ) -> float:
        """
        Calcula média ponderada.

        Cada confiança possui
        um peso associado.
        """

        if not scores:

            return 0.0

        numerator = sum(

            score.value * weight

            for score, weight

            in scores

        )

        denominator = sum(

            weight

            for _, weight

            in scores

        )

        if denominator == 0:

            return 0.0

        return numerator / denominator

    # ------------------------------------------------------
    # Evolution
    # ------------------------------------------------------

    @staticmethod
    def increase(
        current: float,
        evidence_strength: float
    ) -> float:
        """
        Incrementa a confiança
        com base em nova evidência.
        """

        result = (

            current +

            evidence_strength *

            (1.0 - current)

        )

        return ConfidenceClassifier.normalize(
            result
        )

    @staticmethod
    def decrease(
        current: float,
        contradiction_strength: float
    ) -> float:
        """
        Reduz a confiança
        diante de evidências
        contraditórias.
        """

        result = (

            current *

            (

                1.0 -

                contradiction_strength

            )

        )

        return ConfidenceClassifier.normalize(
            result
        )

    # ------------------------------------------------------
    # Merge
    # ------------------------------------------------------

    @staticmethod
    def combine(
        evidences: list[ConfidenceScore]
    ) -> ConfidenceScore:
        """
        Combina diversas evidências
        em um único ConfidenceScore.

        Estratégia atual:

        Média simples.

        Futuramente poderá utilizar:

        - Bayesian Update

        - Dempster-Shafer

        - Fuzzy Logic

        - Consensus Engine
        """

        value = ConfidenceCalculator.average(
            evidences
        )

        return ConfidenceFactory.create(
            value
        )

    # ------------------------------------------------------
    # Extremes
    # ------------------------------------------------------

    @staticmethod
    def maximum(
        scores: list[ConfidenceScore]
    ) -> ConfidenceScore | None:
        """
        Retorna o maior nível
        de confiança.
        """

        if not scores:

            return None

        return max(

            scores,

            key=lambda score:
            score.value

        )

    @staticmethod
    def minimum(
        scores: list[ConfidenceScore]
    ) -> ConfidenceScore | None:
        """
        Retorna o menor nível
        de confiança.
        """

        if not scores:

            return None

        return min(

            scores,

            key=lambda score:
            score.value

        )
# ==========================================================
# Confidence History
# ==========================================================


@dataclass(frozen=True)
class ConfidenceChange:
    """
    Representa uma alteração
    no nível de confiança.
    """

    previous: float

    new: float

    reason: str

    source: str = "KALATRACE"

    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    @property
    def difference(self) -> float:
        """
        Diferença entre os valores.
        """

        return self.new - self.previous

    def to_dict(self):

        return {

            "previous": self.previous,

            "new": self.new,

            "difference": self.difference,

            "reason": self.reason,

            "source": self.source,

            "created_at":
                self.created_at.isoformat()

        }


# ==========================================================
# Confidence History Manager
# ==========================================================


@dataclass
class ConfidenceHistory:
    """
    Mantém o histórico completo
    da evolução da confiança.
    """

    changes: list[ConfidenceChange] = field(
        default_factory=list
    )

    def add_change(
        self,
        change: ConfidenceChange
    ) -> None:

        self.changes.append(change)

    def latest(
        self
    ) -> ConfidenceChange | None:

        if not self.changes:
            return None

        return self.changes[-1]

    def first(
        self
    ) -> ConfidenceChange | None:

        if not self.changes:
            return None

        return self.changes[0]

    @property
    def current(self) -> float:

        latest = self.latest()

        if latest is None:
            return 0.0

        return latest.new

    @property
    def evolution(self) -> float:

        if len(self.changes) < 2:
            return 0.0

        return (
            self.changes[-1].new -
            self.changes[0].previous
        )

    def clear(self):

        self.changes.clear()

    def to_list(self):

        return [

            change.to_dict()

            for change in self.changes

        ]


# ==========================================================
# Confidence Factory
# ==========================================================


class ConfidenceFactory:
    """
    Fábrica oficial de ConfidenceScore.
    """

    DEFAULT_CONFIDENCE = 0.50

    @classmethod
    def create(
        cls,
        value: float | None = None
    ) -> ConfidenceScore:

        if value is None:

            value = cls.DEFAULT_CONFIDENCE

        return ConfidenceScore(
            value=value
        )

    @classmethod
    def weak(cls):

        return cls.create(0.10)

    @classmethod
    def moderate(cls):

        return cls.create(0.40)

    @classmethod
    def strong(cls):

        return cls.create(0.70)

    @classmethod
    def very_strong(cls):

        return cls.create(0.95)


def validate_confidence(confidence: ConfidenceScore) -> bool:
    """
    Valida se o objeto é uma instância de ConfidenceScore.

    ConfidenceScore já valida seu próprio valor (0.0-1.0) em
    __post_init__ no momento da construção, então uma instância
    existente já é válida por definição — esta função apenas
    confirma o tipo.
    """

    if not isinstance(confidence, ConfidenceScore):
        raise TypeError(
            "Objeto informado não é uma instância de ConfidenceScore"
        )

    return True


__all__ = [
    "ConfidenceScore",
    "ConfidenceLevel",
    "ConfidenceFactory",
    "validate_confidence"
]
