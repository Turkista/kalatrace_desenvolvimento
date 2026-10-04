"""
KALATRACE Knowledge - Modelos de domínio epistemológico

Pacote com os modelos de dados centrais do conhecimento científico
do KALATRACE.

IMPLEMENTADOS (em uso ativo):
- iec.py       -> IEC (Informational Epistemic Cell), unidade básica
                  de conhecimento. Consumido por engines/, app.py,
                  run.py, api/main.py.
- evidence.py  -> Evidence, unidade de sustentação epistemológica de
                  um IEC.

PLACEHOLDERS (0 bytes, não implementados):
- concept.py
- discovery.py
- hypothesis.py
- knowledge_node.py
- relationship.py
- scientific_question.py

Achado (sessão 04/08/2026, roadmap de estabilização, seção T1.2b/c):
uma sessão anterior sinalizou knowledge/knowledge_node.py como
"possível duplicação sem ADR" frente a graph/knowledge/knowledge_node.py
(a classe KnowledgeNode real, com 487 linhas, usada pelo Knowledge
Graph "rico"). Investigação desta sessão descarta a duplicação: o
arquivo aqui está vazio (0 bytes), sem nenhuma classe definida e sem
nenhum import em todo o projeto (nem em código nem em testes). Não é
uma segunda implementação concorrente - é um placeholder do mesmo tipo
já documentado em graph/discovery/ e inference/{hybrid,symbolic,
probabilistic}/: o nome corresponde à taxonomia de conceitos de
domínio que hypothesis.py, concept.py, relationship.py e
scientific_question.py também sugerem (Hypothesis, Concept,
Relationship, Scientific Question - vocabulário epistemológico citado
no DPI e nos DMIs de Governance/Curation), não um rascunho abandonado
de KnowledgeNode.

Recomendação: manter como placeholder documentado, mesmo tratamento
já dado a graph/discovery/ e inference/*. Nenhuma duplicação real a
resolver; a pendência "possível duplicação" registrada no roadmap
pode ser fechada.
"""
