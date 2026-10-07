from datetime import timezone

from contracts.iec_contract import IECContract
from knowledge.iec import IEC


def test_iec_contract_roundtrip_preserves_epistemic_state():
    iec = IEC(
        id="IEC-ROUNDTRIP-001",
        content="Uma afirmação epistemológica testável.",
        domain="Conhecimento",
        metadata={"title": "Afirmação", "source": "test"},
    )
    iec.set_confidence(0.82)
    iec.update_status("validated")
    iec.add_evidence("EVIDENCE-001")
    iec.add_relation("IEC-RELATED-001")
    iec.version = 3

    contract = iec.to_contract()
    contract.validate()

    restored = IEC.from_contract(contract)

    assert restored.id == iec.id
    assert restored.statement == iec.statement
    assert restored.domain == iec.domain
    assert restored.confidence == iec.confidence
    assert restored.status == iec.status
    assert restored.version == iec.version
    assert restored.evidence_ids == iec.evidence_ids
    assert restored.related_iec_ids == iec.related_iec_ids
    assert restored.metadata["title"] == "Afirmação"
    assert restored.metadata["source"] == "test"
    assert restored.created_at.tzinfo == timezone.utc
    assert restored.updated_at.tzinfo == timezone.utc


def test_contract_roundtrip_preserves_contract_fields():
    contract = IECContract(
        iec_id="IEC-CONTRACT-001",
        title="Contrato",
        statement="Estado persistível.",
        knowledge_type="observacao",
        confidence=0.71,
        status="candidate",
        evidence_ids=["E1", "E2"],
        metadata={
            "version": 4,
            "related_iec_ids": ["IEC-2"],
            "domain": "observacao",
        },
    )

    iec = IEC.from_contract(contract)
    restored = iec.to_contract()

    assert restored.iec_id == contract.iec_id
    assert restored.title == contract.title
    assert restored.statement == contract.statement
    assert restored.knowledge_type == contract.knowledge_type
    assert restored.confidence == contract.confidence
    assert restored.status == contract.status
    assert restored.evidence_ids == contract.evidence_ids
    assert restored.metadata["version"] == 4
    assert restored.metadata["related_iec_ids"] == ["IEC-2"]
    assert restored.metadata["domain"] == "observacao"
