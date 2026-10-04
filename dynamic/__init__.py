"""
KALATRACE Dynamic -- adaptação estratégica

Ver README.md deste pacote para a definição arquitetural completa.

IMPLEMENTADO (em uso), FASE 5 (PROPOSTA), sessão de 09/08/2026:
- dynamic_engine.py -> DynamicEngine, fachada pública.
- strategy_adapter.py -> StrategyAdapter, aplica o ajuste de
  controvérsia sobre o plano do Research Strategy Engine (RSE).

Escopo real: consome ResearchStrategyEngine.build_strategic_plan()
(já existente) e ConsensusEngine.controversial_iecs() (implementado
na mesma sessão) -- não recalcula prioridade do zero, ajusta o
ranking já existente com um critério documentado (ver
StrategyAdapter.CONTROVERSY_BOOST).

Ainda não ligado a StarHouse, Prediction e Simulation, listados no
README como fontes de Dynamic -- nenhum dos três existe no projeto
hoje. Metacognition existe mas não produz sinal estratégico
consumível ainda (ver nota em DynamicEngine).
"""
