"""
KALATRACE Evolution - Evolução estrutural do grafo

Achado (sessão 02/08/2026, T2.2 do roadmap de estabilização):
evolution/ e engines/knowledge_evolution/ (populado na T1.3a, sessão de
03/08/2026, pela migração de core/knowledge_evolution_engine.py) NÃO
são a mesma responsabilidade -- mesmo padrão dos achados de T0.2
(core/lifecycle vs kernel/lifecycle) e T0.5 (validation/validation_engine.py vs
validation/evidence_validation_engine.py, este último movido de
core/validation_engine.py em T1.4b). Fronteira:

- engines/knowledge_evolution/knowledge_evolution_engine.py (desde a
  T1.3a) = evolução epistêmica de um IEC individual: transições de
  estado, histórico, detecção de regressão, direção da evolução.
  Opera sobre UM nó de conhecimento por vez.
- evolution/ (aqui) = evolução ESTRUTURAL do grafo como um todo:
  reforçar/podar arestas por qualidade (evolution/optimizer.py).
  Opera sobre o grafo inteiro, nunca sobre um IEC isolado.

Decisão: manter as duas pastas separadas, sem fusão. Recomenda-se
registrar isso como nota complementar à ADR-002 (Knowledge Graph
único) ou como ADR própria na T3.6, já que muda o escopo do que a
"unificação de evolução" significa (não existe conflito a resolver,
só nomenclatura próxima).

Nota lateral: evolution/optimizer.py foi escrito contra a API leve
do grafo (graph/knowledge_graph.py, self.edges como lista de dicts)
-- o mesmo tipo de acoplamento já identificado em T0.4/T0.5 para
validation/validation_engine.py. Quando a T1.2 (Graph único) rodar,
optimizer.py precisará do mesmo tipo de adaptação para a versão rica.

Os demais arquivos desta pasta (evolution_tracker.py, history.py,
snapshots.py) seguem vazios (0 bytes) -- placeholders sem código,
não avaliados nesta sessão.
"""
