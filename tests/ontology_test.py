from ontology.ontology import CORE_ONTOLOGY
from shared.enums import EdgeType, NodeType, RelationshipType


def test_core_ontology_metadata_and_classes():
    assert CORE_ONTOLOGY.metadata.version == "0.1"
    assert CORE_ONTOLOGY.has_class(NodeType.IEC)
    assert CORE_ONTOLOGY.has_class(NodeType.EVIDENCE)
    assert CORE_ONTOLOGY.has_class(NodeType.QUESTION)
    assert not CORE_ONTOLOGY.has_class("not_a_node")


def test_core_ontology_reuses_existing_predicate_vocabulary():
    assert CORE_ONTOLOGY.has_predicate(EdgeType.SUPPORTS.value)
    assert CORE_ONTOLOGY.has_predicate(RelationshipType.CAUSES.value)
    assert not CORE_ONTOLOGY.has_predicate("invented_relation")


def test_known_high_confidence_relation_is_valid():
    assert CORE_ONTOLOGY.check_relation(
        NodeType.EVIDENCE,
        EdgeType.SUPPORTS.value,
        NodeType.HYPOTHESIS,
    ) == "VALID"


def test_known_constrained_relation_can_be_invalid():
    assert CORE_ONTOLOGY.check_relation(
        NodeType.QUESTION,
        EdgeType.SUPPORTS.value,
        NodeType.DOCUMENT,
    ) == "INVALID"


def test_known_but_unconstrained_relation_is_unknown():
    assert CORE_ONTOLOGY.check_relation(
        NodeType.CONCEPT,
        RelationshipType.CAUSES.value,
        NodeType.DISCOVERY,
    ) == "UNKNOWN"


def test_unknown_relation_is_unknown_and_does_not_block_flow():
    assert CORE_ONTOLOGY.check_relation(
        NodeType.CONCEPT,
        "future_domain_predicate",
        NodeType.DISCOVERY,
    ) == "UNKNOWN"
