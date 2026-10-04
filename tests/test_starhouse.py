"""Tests for StarHouse — Blueprint 3.0 knowledge cartography stage."""

from knowledge.iec import IEC
from graph.knowledge_graph import KnowledgeGraph
from starhouse import StarHouseEngine


def _graph() -> KnowledgeGraph:
    graph = KnowledgeGraph()
    a = IEC("iec-a", "Bakuchiol", domain="cosmetology")
    b = IEC("iec-b", "Collagen", domain="cosmetology")
    c = IEC("iec-c", "Astrophysics", domain="physics")
    graph.add_node(a)
    graph.add_node(b)
    graph.add_node(c)
    graph.add_edge("iec-a", "iec-b", relation_type="supports", confidence=0.8)
    graph.add_edge("iec-b", "iec-a", relation_type="related", confidence=0.2)
    return graph


def test_observation_builds_regions_and_connections():
    result = StarHouseEngine(_graph()).observe()

    assert result.node_count == 3
    assert result.edge_count == 2
    assert len(result.regions) == 2
    assert len(result.connections) == 2
    assert result.provenance["scientific_truth_evaluation"] == "not_performed"


def test_isolated_nodes_are_reported_as_structural_gap():
    result = StarHouseEngine(_graph()).observe()

    assert result.isolated_node_ids == ["iec-c"]
    assert any(gap.gap_type == "isolated_region" for gap in result.gaps)


def test_low_confidence_connections_are_reported_without_validation():
    result = StarHouseEngine(_graph()).observe()

    assert result.low_confidence_edge_count == 1
    assert any(gap.gap_type == "weak_connection" for gap in result.gaps)


def test_starhouse_does_not_mutate_graph():
    graph = _graph()
    before = graph.stats().copy()
    StarHouseEngine(graph).observe()

    assert graph.stats() == before


def test_health_and_stats():
    engine = StarHouseEngine(_graph())
    engine.observe()

    assert engine.health_check()["status"] == "healthy"
    assert engine.stats()["observations"] == 1
    assert engine.stats()["version"] == "1.0.0"
