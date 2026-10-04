from graph.knowledge_graph import KnowledgeGraph
from graph.base.node import Node
from ontology.ontology import CORE_ONTOLOGY
from validation.ontology_validator import (
    INVALID,
    UNKNOWN,
    VALID,
    OntologyValidator,
)


def make_node(node_id, node_type):
    return Node(node_id, node_type, node_id)


def test_valid_relation_is_reported_without_mutation():
    validator = OntologyValidator()
    result = validator.validate_relation("evidence", "supports", "hypothesis")
    assert result["status"] == VALID


def test_invalid_constrained_relation_is_reported():
    validator = OntologyValidator()
    result = validator.validate_relation("question", "supports", "hypothesis")
    assert result["status"] == INVALID


def test_unknown_relation_does_not_block():
    validator = OntologyValidator()
    result = validator.validate_relation("concept", "causes", "discovery")
    assert result["status"] == UNKNOWN


def test_graph_validation_is_read_only():
    graph = KnowledgeGraph()
    source = make_node("e1", "evidence")
    target = make_node("h1", "hypothesis")
    graph.nodes[source.node_id] = source
    graph.nodes[target.node_id] = target
    graph.add_edge("e1", "h1", "supports", confidence=0.4)

    before_edges = [dict(edge) for edge in graph.edges]
    before_nodes = dict(graph.nodes)

    result = OntologyValidator(CORE_ONTOLOGY).validate_graph(graph)

    assert result["total"] == 1
    assert result["valid"] == 1
    assert result["invalid"] == 0
    assert result["unknown"] == 0
    assert graph.edges == before_edges
    assert graph.nodes == before_nodes


def test_missing_graph_node_is_unknown():
    graph = KnowledgeGraph()
    graph.add_edge("missing", "also_missing", "supports")
    result = OntologyValidator().validate_graph(graph)
    assert result["unknown"] == 1
