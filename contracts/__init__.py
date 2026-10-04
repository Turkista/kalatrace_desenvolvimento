"""
KALATRACE Contracts - Contratos de dados (não arquitetura)

Decisão e execução (sessão 02/08/2026, T2.1 do roadmap de
estabilização): contracts/ e core/contracts/ NÃO disputam a mesma
responsabilidade -- a suposição original do roadmap ("recomendo
contracts/, por já ter DMI") foi corrigida depois de checar o uso
real no código:

- contracts/ (aqui) = contratos de DADOS: EvidenceContract e
  IECContract, dataclasses ativamente usadas em praticamente toda a
  base (core/, engines/, knowledge/, storage/).
- core/contracts/ = contratos de COMPORTAMENTO/ARQUITETURA:
  LifecycleContract, ModuleContract, EngineContract, ServiceContract,
  CommandContract, MissionContract, RepositoryContract -- ABCs usadas
  internamente por core/ para implementar seus próprios componentes.
  Nenhum uso externo a core/ foi encontrado.

Achado: contracts/ também tinha 9 arquivos ABC (agent.py, engine.py,
graph.py, manager.py, parser.py, repository.py, service.py,
storage.py, validator.py) que duplicavam em conceito os contratos de
core/contracts/ -- mas sem NENHUMA referência em todo o projeto,
nem mesmo em testes. Código morto desde antes desta sessão.
Removidos nesta sessão.

Fonte de verdade resultante:
- contracts/ = camada de dados (Evidence, IEC).
- core/contracts/ = camada de comportamento/arquitetura, escopo
  interno a core/.

Recomenda-se registrar esta decisão formalmente como ADR na T3.6,
junto com a atualização do DMI-CONTRATOS (T3.3) prevista no roadmap.
"""
