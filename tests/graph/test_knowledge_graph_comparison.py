"""
T0.4 — Testes comparativos entre as duas versões do Knowledge Graph.

  * "leve":  graph/knowledge_graph.py           (144 linhas, nós/arestas em dict cru)
  * "rica":  graph/knowledge/knowledge_graph.py  (879+ linhas, nós/arestas tipados)

Objetivo do roadmap para T0.4: saber se a versão "leve" tem algum
comportamento que a "rica" não cobre, antes de apagar a leve (T1.2).

Achado original (T0.4): a versão rica NÃO era um superconjunto estrito
da leve. Três métodos de conveniência existiam só na leve:

    - neighbors(node_id)              -> nós vizinhos diretos
    - isolated_nodes()                -> nós sem nenhuma aresta
    - low_confidence_edges(threshold) -> arestas fracas

O achado mais importante: `isolated_nodes()` NÃO era código morto -- é
chamado ativamente por validation/validation_engine.py
(system_quality_score) e por curation/curation.py (detect_gaps).

Atualização (T1.2a, sessão de 02/08/2026): os três métodos foram
portados para a versão rica (graph/knowledge/knowledge_graph.py),
mantendo a mesma semântica -- ver testes de equivalência abaixo, que
substituem os antigos testes "not hasattr". T1.2b (migrar os
consumidores da versão leve, hoje maioria: app.py, run.py, api/main.py,
curation/, evolution/, engines/reasoning/, validation/) e T1.2c (apagar
a versão leve) continuam pendentes -- ver nota de risco no roadmap.
"""

import pytest

from graph.knowledge_graph import KnowledgeGraph as LightKnowledgeGraph

# graph/knowledge/ foi arquivado em _archive/graph_knowledge/ (roadmap de
# estabilização, sessão de 07/08/2026) -- nunca teve consumidor de
# produção; ver _archive/README.md para a justificativa completa. Este
# teste comparativo continua válido e é só o import que mudou.
from _archive.graph_knowledge.knowledge_graph import KnowledgeGraph as RichKnowledgeGraph
from _archive.graph_knowledge.knowledge_node import KnowledgeNode
from _archive.graph_knowledge.knowledge_edge import KnowledgeEdge


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class _FakeIEC:
    """Objeto mínimo aceito pela versão leve (duck typing: só usa .id)."""

    def __init__(self, node_id):
        self.id = node_id


@pytest.fixture
def light_graph():
    g = LightKnowledgeGraph()
    g.add_node(_FakeIEC("a"))
    g.add_node(_FakeIEC("b"))
    g.add_node(_FakeIEC("c"))  # fica isolado (sem arestas)
    g.add_edge("a", "b", relation_type="supports", weight=1.0, confidence=0.2)
    return g


@pytest.fixture
def rich_graph():
    g = RichKnowledgeGraph()
    g.add_node(KnowledgeNode(node_id="a", node_type="IEC", label="A"))
    g.add_node(KnowledgeNode(node_id="b", node_type="IEC", label="B"))
    g.add_node(KnowledgeNode(node_id="c", node_type="IEC", label="C"))  # isolado
    g.add_edge(
        KnowledgeEdge(
            edge_id="e1",
            source_id="a",
            target_id="b",
            relation_type="SUPPORTED_BY",
            confidence=0.2,
        )
    )
    return g


# ---------------------------------------------------------------------------
# Comportamento equivalente nas duas versões
# ---------------------------------------------------------------------------

def test_add_and_get_node_equivalent(light_graph, rich_graph):
    assert light_graph.get_node("a") is not None
    assert rich_graph.get_node("a") is not None
    assert light_graph.get_node("zzz") is None
    assert rich_graph.get_node("zzz") is None


def test_edges_of_vs_get_edges_for_node_equivalent(light_graph, rich_graph):
    # "edges_of" (leve) e "get_edges_for_node" (rica) têm o mesmo contrato.
    light_edges = light_graph.edges_of("a")
    rich_edges = rich_graph.get_edges_for_node("a")

    assert len(light_edges) == 1
    assert len(rich_edges) == 1
    assert light_edges[0]["source"] == "a"
    assert rich_edges[0].source_id == "a"


def test_remove_node_cascades_edges_in_both(light_graph, rich_graph):
    light_graph.remove_node("a")
    assert light_graph.get_node("a") is None
    assert light_graph.edges_of("b") == []

    rich_graph.remove_node("a")
    assert rich_graph.get_node("a") is None
    assert rich_graph.get_edges_for_node("b") == []


# ---------------------------------------------------------------------------
# Métodos portados na T1.2a — agora equivalentes nas duas versões
# ---------------------------------------------------------------------------

def test_neighbors_equivalent(light_graph, rich_graph):
    light_neighbors = light_graph.neighbors("a")
    rich_neighbors = rich_graph.neighbors("a")

    assert [n.id for n in light_neighbors] == ["b"]
    assert [n.node_id for n in rich_neighbors] == ["b"]


def test_isolated_nodes_equivalent(light_graph, rich_graph):
    light_isolated = light_graph.isolated_nodes()
    rich_isolated = rich_graph.isolated_nodes()

    assert [n.id for n in light_isolated] == ["c"]
    assert [n.node_id for n in rich_isolated] == ["c"]


def test_low_confidence_edges_equivalent(light_graph, rich_graph):
    light_weak = light_graph.low_confidence_edges(threshold=0.3)
    rich_weak = rich_graph.low_confidence_edges(threshold=0.3)

    assert len(light_weak) == 1
    assert light_weak[0]["confidence"] == 0.2

    assert len(rich_weak) == 1
    assert rich_weak[0].confidence == 0.2


# ---------------------------------------------------------------------------
# Diferenças estruturais de API (não são bugs, são trade-offs de design)
# ---------------------------------------------------------------------------

def test_light_accepts_loose_typed_edges_rich_requires_objects():
    """
    A versão leve aceita quaisquer parâmetros soltos em add_edge()
    (duck typing, sem validação de tipo de relação). A versão rica
    exige um objeto KnowledgeEdge já validado (relation_type não pode
    ser vazio, confidence precisa estar em [0,1], nós de origem/destino
    precisam existir previamente no grafo). Isto é uma escolha de design
    deliberada da versão rica (mais rígida), não uma lacuna funcional.
    """

    light = LightKnowledgeGraph()
    light.add_node(_FakeIEC("x"))
    light.add_node(_FakeIEC("y"))
    # aceita relation_type arbitrário, minúsculo, sem checagem:
    light.add_edge("x", "y", relation_type="qualquer_coisa")
    assert light.edges_of("x")[0]["type"] == "qualquer_coisa"

    rich = RichKnowledgeGraph()
    rich.add_node(KnowledgeNode(node_id="x", node_type="IEC", label="X"))
    # rejeita edge apontando para nó inexistente (referência íntegra):
    with pytest.raises(ValueError):
        rich.add_edge(
            KnowledgeEdge(
                edge_id="e_bad",
                source_id="x",
                target_id="does_not_exist",
                relation_type="RELATED_TO",
            )
        )


def test_rich_has_no_weight_concept_on_edges():
    """
    A versão leve guarda um "weight" (float) por aresta, além de
    confidence. A versão rica (KnowledgeEdge) não tem esse atributo --
    só confidence e evidence_level. Se algum consumidor da leve depende
    de "weight" (fora dos testes já existentes), isso também precisa
    ser considerado na fusão da T1.2.
    """

    edge = KnowledgeEdge(
        edge_id="e1", source_id="a", target_id="b", relation_type="RELATED_TO"
    )
    assert not hasattr(edge, "weight")
