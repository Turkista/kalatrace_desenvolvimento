from engines.cognitive_orchestrator.cognitive_orchestrator_engine import CognitiveOrchestrator


def test_orchestrator_exposes_starhouse_observation():
    orchestrator = CognitiveOrchestrator()
    result = orchestrator.observe_knowledge_map()

    assert result["version"] == "1.0.0"
    assert result["provenance"]["module"] == "StarHouse"
    assert result["provenance"]["graph_mutated"] is False
