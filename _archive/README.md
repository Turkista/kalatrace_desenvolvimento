# _archive/

Código movido para cá, fora do caminho de import normal do
projeto, mas preservado (não apagado) para referência histórica --
mesmo princípio geral do DOCUMENTO 30 ("histórico nunca é apagado")
aplicado a decisões de arquitetura, não só a dados.

## graph_knowledge/ (antigo graph/knowledge/)

Movido em 07/08/2026 (roadmap de estabilização, decisão sobre o
destino de graph/base/graph.py e graph/knowledge/, sessão de
06-07/08/2026).

Continha uma segunda implementação de grafo ("rica"): KnowledgeNode,
KnowledgeEdge, KnowledgeGraph, KnowledgePath, EvidenceNode -- 487
linhas só em knowledge_node.py.

Motivo do arquivamento: nunca teve nenhum consumidor de produção
(confirmado por busca exaustiva no código antes da decisão). O
docstring de graph/base/graph.py::Graph já definia o papel esperado
para uma camada como esta -- "Regras científicas pertencem às
camadas superiores: KnowledgeGraph, DiscoveryGraph, OntologyGraph..."
-- ou seja, deveria ter sido construída *sobre* graph/base/Node e
graph/base/Graph. Em vez disso, inventou sua própria fundação do
zero (KnowledgeNode, sem nenhuma relação com graph/base/Node),
duplicando a camada estrutural em vez de estender a camada
epistemológica sobre ela.

Nenhum documento oficial do projeto (incluindo o DOCUMENTO 72 --
Domain Model & Engineering Contracts, a especificação de engenharia
mais autoritativa consultada) menciona o nome "KnowledgeNode".

Se uma camada de grafo com regras epistemológicas for construída no
futuro, o caminho recomendado é uma nova classe herdando de
graph.base.graph.Graph (usando graph.base.node.Node, do qual IEC já
herda -- ver knowledge/iec.py) -- não reaproveitar o código aqui
arquivado.

Os testes tests/graph/test_knowledge_graph_comparison.py e
tests/validation/test_validation_engine_comparison.py (que
compararam esta implementação com a versão "leve" em uso, T1.2a/
T1.4a) foram atualizados para importar deste novo caminho e
continuam passando.
