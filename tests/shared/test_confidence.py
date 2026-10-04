"""
KALATRACE Shared - Confidence Smoke Tests

Sessão 02/08/2026. Bug encontrado via pyflakes: shared/confidence.py
tinha DUAS definições de ConfidenceFactory (mesmo padrão do bug já
corrigido em contracts/evidence_contract.py na T0.5) - a segunda,
ativa por último em Python, referenciava um tipo "Confidence" que
não existe em lugar nenhum do arquivo (o tipo real se chama
ConfidenceScore). validate_confidence() tinha o mesmo problema, além
de chamar confidence.validate(), método que ConfidenceScore não tem
(a validação already acontece em __post_init__, na construção).

Nenhum ponto do projeto importava de shared.confidence antes desta
correção (achado confirmado por busca), então o bug nunca havia sido
notado em produção - mas quebraria assim que alguém tentasse usar.

Não pretende ser cobertura completa - o objetivo é detectar
regressão óbvia se algo for quebrado ao mexer no módulo.
"""

import pytest

from shared.confidence import (
    ConfidenceScore,
    ConfidenceFactory,
    ConfidenceLevel,
    validate_confidence,
)


class TestConfidenceScore:
    def test_valid_value_constructs(self):
        score = ConfidenceScore(value=0.8)
        assert score.value == 0.8

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            ConfidenceScore(value=1.5)
        with pytest.raises(ValueError):
            ConfidenceScore(value=-0.1)

    def test_level_property_classifies(self):
        assert ConfidenceScore(value=0.95).level == ConfidenceLevel.VERY_STRONG


class TestConfidenceFactory:
    def test_create_with_explicit_value(self):
        score = ConfidenceFactory.create(0.8)
        assert isinstance(score, ConfidenceScore)
        assert score.value == 0.8

    def test_create_with_default_value(self):
        score = ConfidenceFactory.create()
        assert score.value == ConfidenceFactory.DEFAULT_CONFIDENCE

    def test_weak_moderate_strong_very_strong_shortcuts(self):
        assert ConfidenceFactory.weak().value == 0.10
        assert ConfidenceFactory.moderate().value == 0.40
        assert ConfidenceFactory.strong().value == 0.70
        assert ConfidenceFactory.very_strong().value == 0.95

    def test_only_one_confidencefactory_class_is_exported(self):
        # Regressao: garante que a classe duplicada nao volte a existir
        # (contrato minimo: create() aceita value=None por padrao).
        score = ConfidenceFactory.create(value=None)
        assert isinstance(score, ConfidenceScore)


class TestValidateConfidence:
    def test_valid_confidence_score_returns_true(self):
        score = ConfidenceScore(value=0.5)
        assert validate_confidence(score) is True

    def test_non_confidence_score_raises_typeerror(self):
        with pytest.raises(TypeError):
            validate_confidence("not a confidence score")
