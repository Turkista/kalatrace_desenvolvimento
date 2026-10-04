# DMI — SIMULATION

**Version:** 1.0.0

## Responsabilidade

Simulation é o laboratório virtual de experimentação do KALATRACE. Cria cenários hipotéticos, aplica mudanças isoladas e compara respostas simuladas sem alterar o conhecimento oficial.

## Entradas

- hipóteses e mudanças hipotéticas;
- sinais de Prediction;
- caminhos de Horse;
- cartografia de StarHouse.

## Saídas

- cenários virtuais;
- mudanças aplicadas;
- resultados/observações simuladas;
- pressupostos e incerteza;
- proveniência e advertências.

## Invariantes

1. Não modifica o `KnowledgeGraph`.
2. Não valida hipóteses ou evidências.
3. Não transforma resultados simulados em conhecimento oficial.
4. Não afirma causalidade.
5. Resultados são explicitamente hipotéticos.

## Integração

O Cognitive Orchestrator é a fronteira de comunicação. Simulation pode consumir Prediction, Horse e StarHouse; a incorporação epistemológica permanece fora do módulo.
