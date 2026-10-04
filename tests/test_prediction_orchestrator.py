from engines.cognitive_orchestrator.cognitive_orchestrator_engine import CognitiveOrchestrator


def test_orchestrator_exposes_prediction():
    orchestrator=CognitiveOrchestrator()
    assert orchestrator.health_check()["modules"]["prediction_engine"] is True
    assert "prediction" in orchestrator.stats()
    result=orchestrator.predict_knowledge(statement="climate adaptation")
    assert "scenarios" in result
    assert result["provenance"]["module"] == "Prediction"
