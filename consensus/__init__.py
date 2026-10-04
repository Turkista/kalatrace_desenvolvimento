"""
KALATRACE Consensus -- análise de consenso e divergência científica

Ver README.md deste pacote para a definição arquitetural completa
(função, responsabilidade, comunicação com outros módulos,
limitações).

IMPLEMENTADO (em uso), FASE 5 (PROPOSTA), sessão de 09/08/2026:
- consensus_engine.py -> ConsensusEngine, fachada pública.
- consensus_tracker.py -> ConsensusTracker, histórico de
  classificações de consenso por IEC e detecção de mudança.

Escopo real desta implementação: consome o Panorama Científico já
produzido pela Scientific Context Reconstruction (SCR,
engines/scientific_context/), especificamente o campo
`scientific_consensus` (Seção 15.6) e as listas de evidência
convergente/divergente (15.1/15.2) -- não recalcula consenso, não
julga controvérsia entre pesquisadores reais (o projeto não modela
autoria/afiliação). Ver ConsensusEngine.NOT_DETERMINABLE para o que
fica explicitamente fora do escopo, em vez de fabricado.

Ainda não ligado a Prediction, Simulation e Metacognition, listados
no README como consumidores de Consensus -- nenhum dos três existe
no projeto hoje.
"""
