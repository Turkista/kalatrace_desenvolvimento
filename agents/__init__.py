"""
KALATRACE Agents -- camada de agentes de IA

DOCUMENTO 6 (Arquitetura de Acoplamento de Inteligência
Artificial do Sistema KALATRACE), Título III "Dos Agentes de
Inteligência". Documento 7 (Relatório de Simulação Multiagente)
explicitamente aponta que a arquitetura está no Documento 6, não
nele.

IMPLEMENTADOS (em uso, sessão de 09/08/2026):
- base_agent.py -> Agent, AgentRole (ESTRUTURAL/CRITICO, Art. 4º),
  OutputType (Art. 2º: toda saída de agente é classificada como
  hipótese/interpretação/sugestão/análise crítica/proposta
  estrutural, nunca texto solto).
- agent_registry.py -> AgentRegistry, exige a documentação por
  agente prevista no Art. 4º (finalidade/escopo/entradas/saídas/
  critérios de atuação).
- curiosity_agent.py -> CuriosityAgent (ESTRUTURAL), envolve
  CuriosityEngine.
- reasoning_agent.py -> ReasoningAgent (CRITICO), envolve
  ReasoningEngine.
- validation_agent.py -> ValidationAgent (CRITICO), envolve
  ValidationEngine.
- research_agent.py -> ResearchAgent (ESTRUTURAL), envolve
  ScientificResearchEngine.

Escopo honesto: estes 4 agentes empacotam a saída de Engines já
determinísticos e reais no formato de saída exigido pelo Art. 2º
-- não chamam um modelo de linguagem de verdade (GPT ou Claude
reais). Este ambiente de execução não tem acesso à rede para
chamar uma API de IA externa. Ver o docstring de Agent para mais
detalhes.

Conectados de forma incremental, não em bloco (decisão do
usuário, sessão de 09/08/2026): os 4 agentes acima envolvem
Engines já estáveis e prontos; nenhum foi ligado ao Cognitive
Orchestrator (engines/cognitive_orchestrator/) -- são utilizáveis
de forma independente, e Art. 8º (nenhum agente se comunica
direto com outro) já é respeitado por eles não se referenciarem
entre si.

PLACEHOLDER (0 bytes, não implementado):
- orchestrator_agent.py -> o "Orquestrador Cognitivo" de IA
  (DOCUMENTO 6, Título IV, Camada 3) -- coordenaria os agentes
  (seleção, ordem, limite de interações, consolidação, registro
  de conflitos entre agentes, Art. 5º-9º). Distinto do
  CognitiveOrchestrator já implementado (DOCUMENTO 26,
  engines/cognitive_orchestrator/), que coordena Engines
  determinísticos num ciclo científico -- mesmo nome em
  português ("Orquestrador Cognitivo"), documentos e escopos
  diferentes. Deixado por último deliberadamente: o formato do
  ciclo de Engines ainda pode mudar (novos módulos da Arquitetura
  Cognitiva -- ver FASE 5 proposta no roadmap), e um Orquestrador
  de agentes construído cedo demais precisaria ser reescrito a
  cada mudança.
"""
