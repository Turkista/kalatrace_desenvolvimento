from engines.cognitive_orchestrator.cognitive_orchestrator_engine import CognitiveOrchestrator


def test_cycle_pipeline_adds_semantic_validation_without_replacing_structural_validation():
    orchestrator = CognitiveOrchestrator()

    result = orchestrator.run_cycle(
        statement="Uma observação deve ser investigada.",
        submitted_by="ontology-test",
    )

    assert "validation" in result
    assert "semantic_validation" in result
    assert isinstance(result["semantic_validation"], dict)
    assert set(result["semantic_validation"]) >= {
        "total", "valid", "invalid", "unknown", "diagnostics"
    }


def test_cycle_pipeline_semantic_validation_is_read_only():
    orchestrator = CognitiveOrchestrator()

    result = orchestrator.run_cycle(
        statement="Uma segunda observação deve preservar o grafo.",
        submitted_by="ontology-test",
    )

    semantic = result["semantic_validation"]
    assert semantic["total"] == len(orchestrator.graph.edges)
    assert semantic["total"] == len(semantic["diagnostics"])
