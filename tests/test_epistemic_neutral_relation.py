"""Regression coverage for neutral epistemic relations in the HTTP projection."""
import os
from types import SimpleNamespace

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test-publishable-key")
os.environ.setdefault("KALATRACE_AUTH_REQUIRED", "false")
os.environ.setdefault("NEO4J_ENABLED", "false")

from fastapi.testclient import TestClient

from api import main as api_main


IEC_ID = "00000000-0000-0000-0000-000000000001"


class NeutralEvidence:
    evidence_id = "EV-NEUTRAL"
    title = "Evidence without directional support"
    confidence = 0.6

    def to_dict(self):
        return {"id": self.evidence_id, "title": self.title, "confidence": self.confidence}


class NeutralEvidenceStore:
    def compute_epistemic_synthesis(self, iec_id):
        return {
            "relations": [{
                "id": "REL-EV-NEUTRAL",
                "evidence_id": "EV-NEUTRAL",
                "iec_id": iec_id,
                "relation": "NEUTRAL",
                "weight": 0.5,
                "reason": "It does not support or contradict the statement.",
                "created_at": "2026-10-11T10:00:00+00:00",
                "validated_at": None,
                "metadata": {},
            }],
            "support_score": 0.0,
            "contradiction_score": 0.0,
            "evidence_count": 1,
            "supporting_count": 0,
            "contradicting_count": 0,
            "neutral_count": 1,
        }

    def get_evidence_for_iec(self, iec_id):
        return [NeutralEvidence()]


def test_epistemic_http_route_keeps_neutral_evidence_out_of_directional_lists(monkeypatch):
    monkeypatch.setattr(api_main, "evidence_store", NeutralEvidenceStore())
    monkeypatch.setattr(api_main, "_hydrate_evidence_store_from_supabase", lambda request: None)
    monkeypatch.setattr(
        api_main,
        "_hydrate_iec_from_supabase",
        lambda request, iec_id: SimpleNamespace(
            title="Test IEC",
            statement="Test statement",
            content="Test statement",
            knowledge_type="hypothesis",
            node_type="hypothesis",
            confidence=0.6,
        ),
    )
    monkeypatch.setattr(
        api_main,
        "evidence_validator",
        SimpleNamespace(
            validate_iec=lambda contract: {
                "classification": "INSUFFICIENT",
                "evidence_strength": 0.0,
            },
            analyze_evidence_gaps=lambda contract: {"identified_gaps": []},
            _interpret_strength=lambda classification: f"Interpretation: {classification}",
        ),
    )

    response = TestClient(api_main.app).get(f"/epistemic/iec/{IEC_ID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_state"]["neutral_count"] == 1
    assert payload["current_state"]["supporting_count"] == 0
    assert payload["current_state"]["contradicting_count"] == 0
    assert [item["id"] for item in payload["evidence"]] == ["EV-NEUTRAL"]
    assert payload["supporting_evidence"] == []
    assert payload["contradicting_evidence"] == []
    assert payload["evidence"][0]["epistemic_relation"]["relation"] == "NEUTRAL"
