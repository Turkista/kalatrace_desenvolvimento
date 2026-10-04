"""Tests for PARSI — Blueprint 3.0 cognitive interpretation stage."""

import pytest

from parsi import PARSIEngine


def test_interpretation_extracts_structure_without_validating_truth():
    engine = PARSIEngine()
    result = engine.interpret(
        "Bakuchiol estimula a produção de colágeno tipo I em fibroblastos.",
        source="test",
    )

    assert result.intent == "observation"
    assert result.context.language == "pt"
    assert result.context.modality == "neutral"
    assert result.interpretation_confidence > 0
    assert result.provenance["scientific_truth_evaluation"] == "not_performed"
    assert any(entity.normalized == "bakuchiol" for entity in result.entities)


def test_hypothesis_and_uncertainty_are_structural_signals_only():
    engine = PARSIEngine()
    result = engine.interpret("A hipótese é que o resveratrol pode reduzir a inflamação.")

    assert result.intent == "hypothesis"
    assert result.context.modality == "uncertain"
    assert 0 <= result.interpretation_confidence <= 1
    assert any("não interpreta isso como prova" in warning for warning in result.warnings)


def test_relation_candidates_are_extracted():
    engine = PARSIEngine()
    result = engine.interpret("Bakuchiol reduz inflamação cutânea e estimula colágeno.")

    assert result.relations
    assert any(relation.relation == "negative" for relation in result.relations)


def test_mapping_input_is_supported():
    engine = PARSIEngine()
    result = engine.interpret({"statement": "Colágeno melhora a regeneração da pele."})

    assert result.raw_text.startswith("Colágeno")
    assert result.normalized_text == result.raw_text


def test_empty_input_is_rejected():
    engine = PARSIEngine()
    with pytest.raises(ValueError):
        engine.interpret("   ")


def test_stats_track_interpretations():
    engine = PARSIEngine()
    engine.interpret("A pele responde ao tratamento.")
    engine.interpret("Qual é o efeito?")

    stats = engine.stats()
    assert stats["interpretations"] == 2
    assert stats["version"] == "1.0.0"
    assert stats["intents"]["question"] == 1
