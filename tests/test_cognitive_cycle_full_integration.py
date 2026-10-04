from engines.cognitive_orchestrator.cognitive_orchestrator_engine import CognitiveOrchestrator
from graph.knowledge_graph import KnowledgeGraph
from storage.evidence_store import EvidenceStore


def test_full_cognitive_cycle_integrates_advanced_modules_and_structural_nodes():
    graph = KnowledgeGraph()
    orchestrator = CognitiveOrchestrator(
        graph=graph,
        evidence_store=EvidenceStore(),
    )

    result = orchestrator.run_cycle(
        statement="Bakuchiol apresenta relação experimental com a via SIRT1.",
        submitted_by="integration-test",
        submission_type="observacao",
    )

    assert result["iec"] is not None
    assert result["parsi"] is not None
    assert result["consensus"] is not None
    assert result["hypothesis_candidate"] is not None
    assert result["cycle"]["state"]
    assert len(graph.nodes) == 1
    assert len(graph.knowledge_nodes) == 1

    iec_id = result["iec"].id
    kn = graph.get_knowledge_node(f"knowledge:{iec_id}")
    assert kn is not None
    assert kn.entity_id == iec_id
    assert kn.entity_type == "IEC"
    assert graph.get_node(iec_id) is result["iec"]
