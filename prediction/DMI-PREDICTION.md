# DMI-PREDICTION — Data & Module Interface

## 1. Papel
Prediction é o especialista cognitivo responsável por projetar **cenários probabilísticos** a partir de sinais observáveis já existentes.

## 2. Entradas
- KnowledgeGraph;
- resultado opcional de PARSI;
- mapa opcional de StarHouse;
- exploração opcional de Horse;
- alvo e/ou enunciado.

## 3. Saídas
`PredictionResult` contém sinais, cenários, pressupostos, incerteza e proveniência.

## 4. Limites
Prediction não cria IECs, não modifica o KnowledgeGraph, não valida evidências, não estabelece causalidade e não apresenta seus scores como probabilidades calibradas do mundo real.

## 5. Integração
A comunicação com PARSI, StarHouse e Horse ocorre por contratos explícitos e o Cognitive Orchestrator permanece como fronteira de coordenação.

## 6. Critérios de aceite
- projeções reproduzíveis para os mesmos sinais;
- cenários acompanhados de pressupostos e incerteza;
- proveniência explícita;
- nenhuma mutação do conhecimento;
- testes unitários e integração no orchestrator.
