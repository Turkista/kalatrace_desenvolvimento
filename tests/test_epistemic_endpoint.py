"""Focused tests for the epistemic IEC projection endpoint.

The tests use mocked persistence/validation and never contact Supabase or Neo4j.
"""
import os
from types import SimpleNamespace

# api.main constructs integration clients during import; configure harmless
# local test settings before importing it.
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")
os.environ.setdefault("KALATRACE_AUTH_REQUIRED", "false")
os.environ.setdefault("NEO4J_ENABLED", "false")

import pytest
from fastapi import HTTPException

from api import main as api_main


IEC_ID = "00000000-0000-0000-0000-000000000001"


class FakeEvidence:
    def __init__(self, evidence_id, title, confidence):
        self.evidence_id = evidence_id
        self.title = title
        self.confidence = confidence

    def to_dict(self):
        return {
            "id": self.evidence_id,
            "title": self.title,
            "confidence": self.confidence,
        }


class FakeEvidenceStore:
    def __init__(self, relations=(), evidence=()):
        self._relations = list(relations)
        self._evidence = list(evidence)

    def compute_epistemic_synthesis(self, iec_id):
        relations = [r for r in self._relations if r["iec_id"] == iec_id]
        support = sum(r["relation"] == "SUPPORTS" for r in relations)
        contradict = sum(r["relation"] == "CONTRADICTS" for r in relations)
        neutral = sum(r["relation"] == "NEUTRAL" for r in relations)
        return {
            "relations": relations,
            "support_score": 0.8 if support else 0.0,
            "contradiction_score": 0.7 if contradict else 0.0,
            "evidence_count": len(relations),
            "supporting_count": support,
            "contradicting_count": contradict,
            "neutral_count": neutral,
        }

    def get_evidence_for_iec(self, iec_id):
        related_ids = {
            r["evidence_id"] for r in self._relations if r["iec_id"] == iec_id
        }
        return [e for e in self._evidence if e.evidence_id in related_ids]


def relation(evidence_id, kind):
    return {
        "id": f"REL-{evidence_id}",
        "evidence_id": evidence_id,
        "iec_id": IEC_ID,
        "relation": kind,
        "weight": 0.75,
        "reason": f"Test reason for {kind}",
        "created_at": "2026-10-09T10:00:00+00:00",
        "validated_at": None,
        "metadata": {"test": True},
    }


def setup_projection(monkeypatch, *, iec, relations=(), evidence=()):
    store = FakeEvidenceStore(relations, evidence)
    monkeypatch.setattr(api_main, "evidence_store", store)
    monkeypatch.setattr(api_main, "_hydrate_evidence_store_from_supabase", lambda request: None)
    monkeypatch.setattr(
        api_main,
        "_hydrate_iec_from_supabase",
        lambda request, iec_id: iec,
    )
    monkeypatch.setattr(
        api_main,
        "evidence_validator",
        SimpleNamespace(
            validate_iec=lambda contract: {
                "classification": "MIXED" if any(r["relation"] == "CONTRADICTS" for r in relations) else "INSUFFICIENT",
                "evidence_strength": 0.5 if relations else 0.0,
            },
            analyze_evidence_gaps=lambda contract: {"identified_gaps": []},
            _interpret_strength=lambda classification: f"Interpretation: {classification}",
        ),
    )
    return store


def fake_iec():
    return SimpleNamespace(
        title="IEC de teste",
        statement="Afirmação de teste",
        content="Afirmação de teste",
        knowledge_type="hypothesis",
        node_type="hypothesis",
        confidence=0.6,
    )


def test_epistemic_endpoint_returns_404_for_unknown_iec(monkeypatch):
    monkeypatch.setattr(api_main, "_hydrate_evidence_store_from_supabase", lambda request: None)
    monkeypatch.setattr(api_main, "_hydrate_iec_from_supabase", lambda request, iec_id: None)

    with pytest.raises(HTTPException) as exc:
        api_main.get_epistemic_conclusion(IEC_ID, SimpleNamespace())

    assert exc.value.status_code == 404
    assert IEC_ID in exc.value.detail


def test_epistemic_endpoint_returns_empty_evidence_for_valid_iec(monkeypatch):
    setup_projection(monkeypatch, iec=fake_iec())

    result = api_main.get_epistemic_conclusion(IEC_ID, SimpleNamespace())

    assert result["iec"]["id"] == IEC_ID
    assert result["evidence"] == []
    assert result["supporting_evidence"] == []
    assert result["contradicting_evidence"] == []
    assert result["strongest_evidence"] is None
    assert result["current_state"]["evidence_count"] == 0
    assert result["gaps"] == []


def test_epistemic_endpoint_separates_supporting_and_contradicting_evidence(monkeypatch):
    relations = [relation("EV-SUPPORT", "SUPPORTS"), relation("EV-CONTRA", "CONTRADICTS")]
    evidence = [
        FakeEvidence("EV-SUPPORT", "Supporting evidence", 0.9),
        FakeEvidence("EV-CONTRA", "Contradicting evidence", 0.8),
    ]
    setup_projection(monkeypatch, iec=fake_iec(), relations=relations, evidence=evidence)

    result = api_main.get_epistemic_conclusion(IEC_ID, SimpleNamespace())

    assert result["current_state"]["supporting_count"] == 1
    assert result["current_state"]["contradicting_count"] == 1
    assert [item["id"] for item in result["supporting_evidence"]] == ["EV-SUPPORT"]
    assert [item["id"] for item in result["contradicting_evidence"]] == ["EV-CONTRA"]
    assert result["evidence"][0]["epistemic_relation"]["relation"] == "SUPPORTS"
    assert result["evidence"][1]["epistemic_relation"]["relation"] == "CONTRADICTS"
    assert result["evidence"][0]["epistemic_relation"]["metadata"] == {"test": True}
