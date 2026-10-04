from engines.base.base_engine import CoreEngine
from graph.knowledge_graph import KnowledgeGraph
from horse import HorseEngine
from parsi import PARSIEngine


def make_graph():
    graph=KnowledgeGraph(); engine=CoreEngine()
    graph.add_node(engine.create_iec("a","climate adaptation","Climate"))
    graph.add_node(engine.create_iec("b","agriculture resilience","Agriculture"))
    graph.add_node(engine.create_iec("c","water management","Hydrology"))
    graph.add_node(engine.create_iec("d","crop yield","Agriculture"))
    graph.add_edge("a","b","related",confidence=.9)
    graph.add_edge("b","c","mechanism",confidence=.8)
    graph.add_edge("c","d","related",confidence=.7)
    return graph


def test_horse_explores_non_linear_paths_without_mutation():
    graph=make_graph(); before=(dict(graph.nodes),list(graph.edges))
    result=HorseEngine(graph).explore(seeds=["a"],max_hops=3)
    assert result.paths
    assert any(len(p.node_ids)>=3 for p in result.paths)
    assert graph.nodes==before[0] and graph.edges==before[1]
    assert result.provenance["scientific_validation"]=="not_performed"


def test_horse_uses_parsi_to_resolve_seed():
    graph=make_graph(); parsi=PARSIEngine()
    parsed=parsi.interpret("climate adaptation")
    result=HorseEngine(graph).explore(parsi_result=parsed,max_hops=2)
    assert "a" in result.seed_ids


def test_horse_health_and_stats():
    horse=HorseEngine(make_graph())
    assert horse.health_check()["status"]=="healthy"
    assert horse.stats()["explorations"]==0
