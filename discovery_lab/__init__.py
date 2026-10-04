"""
KALATRACE Discovery Lab -- geração e organização de hipóteses

Ver README.md deste pacote para a definição arquitetural completa.

IMPLEMENTADO (em uso), FASE 5 (PROPOSTA), sessão de 09/08/2026:
- discovery_lab_engine.py -> DiscoveryLabEngine, fachada pública.
- hypothesis_builder.py -> HypothesisBuilder, classifica lacunas +
  conexões do grafo em candidatos a hipótese estruturados.

Escopo real: consome CuriosityEngine.analyze_gap/.generate_questions
(já existentes) e as conexões do grafo já inferidas para a IEC. Não
gera texto de hipótese -- ver HypothesisBuilder para o porquê e
DiscoveryLabEngine.NOT_DETERMINABLE embutido em cada candidato.

Ainda não ligado a Horse, StarHouse, PARSI, Simulation e Prediction,
listados no README como fontes/consumidores de Discovery Lab --
nenhum dos cinco existe no projeto hoje.
"""
