from simulation import SimulationChange, SimulationEngine
from graph.knowledge_graph import KnowledgeGraph


def test_simulation_contract_and_non_mutation():
    graph = KnowledgeGraph()
    engine = SimulationEngine(graph)
    before = graph.stats().copy()
    result = engine.simulate("Test", [SimulationChange("confidence", 0.9)], alternatives=3)
    assert len(result.scenarios) == 3
    assert result.scenarios[0].changes[0].field == "confidence"
    assert result.provenance["graph_mutated"] is False
    assert graph.stats() == before
    assert engine.health_check()["status"] == "healthy"
