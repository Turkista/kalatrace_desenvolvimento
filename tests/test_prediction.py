from engines.base.base_engine import CoreEngine
from graph.knowledge_graph import KnowledgeGraph
from horse import HorseEngine
from parsi import PARSIEngine
from prediction import PredictionEngine
from starhouse import StarHouseEngine


def make_graph():
    g=KnowledgeGraph(); e=CoreEngine()
    g.add_node(e.create_iec("a","climate adaptation","Climate"))
    g.add_node(e.create_iec("b","agriculture resilience","Agriculture"))
    g.add_node(e.create_iec("c","water management","Hydrology"))
    g.add_node(e.create_iec("d","crop yield","Agriculture"))
    g.add_edge("a","b","related",confidence=.9)
    g.add_edge("b","c","mechanism",confidence=.8)
    g.add_edge("c","d","related",confidence=.7)
    return g


def test_prediction_builds_ranked_scenarios_without_mutation():
    g=make_graph(); before=(dict(g.nodes),list(g.edges))
    parsi=PARSIEngine(); parsed=parsi.interpret("climate adaptation")
    star=StarHouseEngine(g).observe(); horse=HorseEngine(g).explore(seeds=["a"],max_hops=3)
    result=PredictionEngine(g).predict(statement="climate adaptation",parsi_result=parsed,starhouse_map=star,horse_exploration=horse)
    assert result.scenarios
    assert result.scenarios[0].probability >= result.scenarios[-1].probability
    assert sum(s.probability for s in result.scenarios) <= 1.000001
    assert g.nodes==before[0] and g.edges==before[1]
    assert result.provenance["scientific_validation"] == "not_performed"


def test_prediction_has_explicit_uncertainty_and_assumptions():
    g=make_graph(); result=PredictionEngine(g).predict(target_id="a")
    assert result.scenarios
    assert all(s.assumptions for s in result.scenarios)
    assert all(0 <= s.uncertainty <= 1 for s in result.scenarios)


def test_prediction_health_and_stats():
    p=PredictionEngine(make_graph())
    assert p.health_check()["status"] == "healthy"
    assert p.stats()["predictions"] == 0
