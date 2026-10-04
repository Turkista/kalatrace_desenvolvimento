"""
T0.5 — Testes de fumaça para validation/validation_engine.py e
validation/evidence_validation_engine.py (movido de
core/validation_engine.py em T1.4b, sessão de 03/08/2026).

O roadmap original tratava estes dois arquivos como um possível caso de
duplicação (mesma classe, ValidationEngine, em dois lugares). Este
teste confirma que NÃO são duplicados funcionais -- são duas
responsabilidades diferentes, como os próprios docstrings já diziam:

  * validation/evidence_validation_engine.py (EvidenceValidationEngine)
      Validação epistemológica baseada em evidências (IECContract +
      EvidenceStore). Não toca o grafo. Não muda estado -- só calcula
      e classifica (INSUFFICIENT/WEAK/MODERATE/STRONG).

  * validation/validation_engine.py (ValidationEngine)
      Validação estrutural do grafo (KnowledgeGraph + EvidenceStore).
      MUTA o nó: recalcula e grava a nova confidence via
      node.update_confidence(). Detecta conflitos estruturais e calcula
      um "system_quality_score" agregando o grafo inteiro.

Conclusão da T1.4a (sessão de 03/08/2026): a fusão prevista pela ADR-003
("comparar regras e escolher uma fonte de verdade") não é o modelo
certo aqui -- os dois arquivos resolvem problemas diferentes e
complementares, confirmado pelos próprios docstrings do código. Ação
tomada na T1.4b: renomeada a classe do arquivo movido para
EvidenceValidationEngine (evita colisão de nome) e os dois motores
mantidos lado a lado, sem fusão. Nenhum consumidor de produção real
usava core/validation_engine.py antes da migração (só api/api.py, já
documentado como legado/quebrado por outros motivos) -- migração de
baixo risco.

Achado crítico (conecta com T0.4): validation/validation_engine.py foi
escrito contra a API da versão LEVE do grafo (graph/knowledge_graph.py),
não a rica (graph/knowledge/knowledge_graph.py):

  - system_quality_score() chama self.graph.isolated_nodes() -- método
    que só existia na versão leve quando este teste foi escrito (T0.5).
    ATUALIZADO NA T1.2a (03/08/2026): isolated_nodes() já foi portado
    para a versão rica, então esta chamada específica não quebra mais
    (ver teste abaixo, atualizado).
  - detect_basic_conflicts() itera "for edge in self.graph.edges" como
    se fosse uma lista de dicts (formato da leve). Na versão rica,
    self.edges é um dict de KnowledgeEdge indexado por edge_id, então
    o for-loop itera sobre as CHAVES (strings) e edge.get(...) explode.
    AINDA QUEBRA -- não foi portado, porque a correção exige uma
    decisão semântica (a leve usa "supports"/"contradicts" minúsculos;
    a rica usa ALLOWED_RELATION_TYPES como "SUPPORTED_BY"/"CONTRADICTS",
    com direção potencialmente invertida) que não é uma adaptação
    mecânica -- fica para quando a T1.2b/c for retomada.

O que realmente precisa acontecer antes de qualquer fusão futura:

  1. ~~Decidir se validation/validation_engine.py continua existindo como
     camada estrutural separada~~ -- decidido na T1.4a/b: sim, continua
     separado.
  2. Migrar validation/validation_engine.py para a API da versão RICA
     do grafo continua pendente -- depende de T1.2b/c (migração dos
     consumidores), que segue não executada por decisão explícita
     (risco avaliado como maior que o benefício imediato, ver roadmap).

Registrado nesta sessão como conclusão da T1.4a/b -- ADR-003 precisa
ser atualizada para refletir "reorganizar, não fundir" (T3.6).
"""

import pytest

from contracts.iec_contract import IECContract
from contracts.evidence_contract import EvidenceContract
from storage.evidence_store import EvidenceStore

from validation.evidence_validation_engine import (
    EvidenceValidationEngine as CoreValidationEngine,
)

# graph/knowledge/ foi arquivado em _archive/graph_knowledge/ (roadmap de
# estabilização, sessão de 07/08/2026) -- nunca teve consumidor de
# produção; ver _archive/README.md para a justificativa completa.
from _archive.graph_knowledge.knowledge_graph import KnowledgeGraph as RichKnowledgeGraph
from _archive.graph_knowledge.knowledge_node import KnowledgeNode
from _archive.graph_knowledge.knowledge_edge import KnowledgeEdge
from validation.validation_engine import (
    ValidationEngine as StructuralValidationEngine,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def evidence_store():
    store = EvidenceStore()
    ev = EvidenceContract(
        id="ev1",
        title="Estudo X",
        description="Descricao",
        evidence_type="clinical",
        confidence=0.8,
    )
    store.add_evidence(ev)
    store.link_to_iec("ev1", "iec-a")
    return store


@pytest.fixture
def iec_a():
    return IECContract(
        iec_id="iec-a",
        title="IEC A",
        statement="Bakuchiol estimula diferenciação de células-tronco.",
        knowledge_type="mechanism",
    )


@pytest.fixture
def rich_graph_with_confidence():
    g = RichKnowledgeGraph()
    g.add_node(
        KnowledgeNode(node_id="iec-a", node_type="IEC", label="A", confidence=0.5)
    )
    g.add_node(
        KnowledgeNode(node_id="iec-b", node_type="IEC", label="B", confidence=0.1)
    )
    g.add_edge(
        KnowledgeEdge(
            edge_id="e1",
            source_id="iec-a",
            target_id="iec-b",
            relation_type="SUPPORTED_BY",
        )
    )
    return g


# ---------------------------------------------------------------------------
# validation/evidence_validation_engine.py — validação epistemológica baseada em evidências
# ---------------------------------------------------------------------------

def test_core_engine_requires_evidence_store_instance():
    with pytest.raises(TypeError):
        CoreValidationEngine(evidence_store="not-a-store")


def test_core_engine_validate_iec_classifies_strength(evidence_store, iec_a):
    engine = CoreValidationEngine(evidence_store=evidence_store)
    result = engine.validate_iec(iec_a)

    assert result["iec_id"] == "iec-a"
    assert result["evidence_count"] == 1
    # 1 evidência com confidence 0.8 -> força média 0.8 -> STRONG (>=0.75)
    assert result["evidence_strength"] == 0.8
    assert result["classification"] == "STRONG"


def test_core_engine_does_not_touch_any_graph(evidence_store, iec_a):
    """
    validation/evidence_validation_engine.py não recebe grafo no construtor -- ele
    trabalha só com IECContract + EvidenceStore. Confirma que a
    responsabilidade é mesmo diferente da validation/validation_engine.py.
    """
    engine = CoreValidationEngine(evidence_store=evidence_store)
    assert not hasattr(engine, "graph")


# ---------------------------------------------------------------------------
# validation/validation_engine.py — validação estrutural do grafo
# ---------------------------------------------------------------------------

def test_structural_engine_requires_graph_and_store(evidence_store):
    with pytest.raises(ValueError):
        StructuralValidationEngine(graph=None, evidence_store=evidence_store)
    with pytest.raises(ValueError):
        StructuralValidationEngine(graph=object(), evidence_store=None)


def test_structural_engine_validate_iec_mutates_node_confidence(
    rich_graph_with_confidence, evidence_store
):
    engine = StructuralValidationEngine(
        graph=rich_graph_with_confidence, evidence_store=evidence_store
    )
    node_before = rich_graph_with_confidence.get_node("iec-a").confidence
    assert node_before == 0.5

    result = engine.validate_iec("iec-a")

    # a fixture evidence_store liga "iec-a" a uma evidência com
    # confidence 0.8; a nova confidence é a média com a antiga (0.5).
    node_after = rich_graph_with_confidence.get_node("iec-a").confidence
    assert node_after == pytest.approx((0.5 + 0.8) / 2)
    assert result["new_confidence"] == node_after


def test_structural_engine_weak_knowledge_reads_graph_nodes(
    rich_graph_with_confidence, evidence_store
):
    engine = StructuralValidationEngine(
        graph=rich_graph_with_confidence, evidence_store=evidence_store
    )
    weak = engine.weak_knowledge(threshold=0.3)
    weak_ids = {n.node_id for n in weak}
    assert weak_ids == {"iec-b"}  # confidence 0.1 < 0.3; iec-a tem 0.5


# ---------------------------------------------------------------------------
# Achado crítico: validation/validation_engine.py está preso à API da
# versão LEVE do grafo, e quebra contra a versão rica.
# ---------------------------------------------------------------------------

def test_structural_engine_system_quality_score_works_on_rich_graph(
    rich_graph_with_confidence, evidence_store
):
    """
    ATUALIZADO NA T1.2a (03/08/2026): isolated_nodes() foi portado para
    a versão rica do grafo, então system_quality_score() -- que só
    dependia desse método para funcionar contra a versão rica -- não
    quebra mais. Este teste substitui o antigo
    test_structural_engine_system_quality_score_breaks_on_rich_graph,
    que afirmava o oposto (achado T0.5, antes da T1.2a).
    """
    engine = StructuralValidationEngine(
        graph=rich_graph_with_confidence, evidence_store=evidence_store
    )
    score = engine.system_quality_score()
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_structural_engine_detect_basic_conflicts_breaks_on_rich_graph(
    rich_graph_with_confidence, evidence_store
):
    """
    detect_basic_conflicts() itera "for edge in self.graph.edges" como
    se self.edges fosse uma lista de dicts (API da versão leve). Na
    versão rica, self.edges é um dict de KnowledgeEdge indexado por
    edge_id, então o loop itera sobre as CHAVES (strings) e
    edge.get(...) explode com AttributeError.

    Diferente de isolated_nodes() (T1.2a), este método NÃO foi portado
    nesta sessão: a correção exige uma decisão semântica, não uma
    adaptação mecânica -- a versão leve usa "supports"/"contradicts"
    (minúsculo), a rica usa ALLOWED_RELATION_TYPES como
    "SUPPORTED_BY"/"CONTRADICTS" (maiúsculo, com direção
    potencialmente invertida: "SUPPORTED_BY" é o inverso semântico de
    "supports"). Fica para quando T1.2b/c for retomada.
    """
    engine = StructuralValidationEngine(
        graph=rich_graph_with_confidence, evidence_store=evidence_store
    )
    with pytest.raises(AttributeError):
        engine.detect_basic_conflicts()


def test_structural_engine_report_breaks_on_rich_graph_via_conflicts(
    rich_graph_with_confidence, evidence_store
):
    """
    report() agrega system_quality_score() (já funciona, T1.2a) e
    detect_basic_conflicts() (ainda quebra) -- por isso report()
    continua quebrando, mas agora só por causa de
    detect_basic_conflicts(), não mais por isolated_nodes().
    """
    engine = StructuralValidationEngine(
        graph=rich_graph_with_confidence, evidence_store=evidence_store
    )
    with pytest.raises(AttributeError):
        engine.report()


# ---------------------------------------------------------------------------
# validation/ tem 4 arquivos vazios além de validation_engine.py
# ---------------------------------------------------------------------------

def test_validation_package_has_empty_sibling_modules():
    """
    Achado histórico T0.5: validation/ possui módulos auxiliares que foram
    placeholders em etapas anteriores. O ontology_validator.py deixou de ser
    placeholder na Fase 2 e agora contém apenas a camada semântica mínima,
    read-only, prevista para a Ontologia v0.1. Os demais módulos auxiliares
    continuam sendo verificados como placeholders nesta comparação.
    """
    import validation.evidence_validator as ev
    import validation.consistency_validator as cv
    import validation.graph_validator as gv
    import validation.ontology_validator as ov

    for module in (ev, cv, gv):
        # Estes módulos continuam placeholders nesta etapa.
        public_names = [n for n in dir(module) if not n.startswith("__")]
        assert public_names == [], f"{module.__name__} não está mais vazio"

    # ontology_validator.py é uma exceção deliberada: foi implantado na
    # Fase 2 como a primeira integração read-only da Ontologia v0.1.
    assert hasattr(ov, "OntologyValidator")
