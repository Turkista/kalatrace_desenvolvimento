"""
KALATRACE Research Strategy -- Research Strategy Engine (RSE)

DOCUMENTO 25 (Research Strategy Engine -- Arquitetura para
Priorização Inteligente da Pesquisa Científica).

IMPLEMENTADOS (em uso):
- research_strategy_engine.py -> ResearchStrategyEngine, fachada
  pública do pacote.
- prioritizer.py -> Prioritizer, pontua oportunidades nos 4
  critérios computáveis do Art. 5º (dos 8 oficiais -- ver docstring
  da classe para os 4 não determináveis com os dados do projeto
  hoje: viabilidade experimental, relevância clínica, potencial
  translacional, sinergia com projetos ativos).
- strategy_generator.py -> StrategyGenerator, gera recomendação de
  próximo passo (Art. 7º), sempre consultiva (Art. 9º).
- planner.py -> ResearchPlanner, organiza oportunidades avaliadas
  em um plano ranqueado (Art. 6º, "Estratégia Adaptativa").

Implementado em 08/08/2026 (roadmap de estabilização) -- terceiro e
último módulo novo construído sobre o Cognitive Orchestrator
(engines/cognitive_orchestrator/), completando os 3 passos do ciclo
oficial (DOCUMENTO 26, Art. 5º) que não tinham módulo real.
"""
