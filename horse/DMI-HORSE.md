# DMI — HORSE

**Versão:** 1.0.0  
**Camada:** Arquitetura Cognitiva  
**Tipo:** Especialista Cognitivo  
**Status:** Implementado

## 1. Finalidade

Horse explora caminhos não lineares no conhecimento já representado, procurando rotas alternativas, conexões improváveis e fronteiras de investigação.

## 2. Entradas

- `KnowledgeGraph`;
- sementes explícitas ou entidades produzidas por PARSI;
- mapa estrutural produzido por StarHouse;
- limite de profundidade e quantidade de caminhos.

## 3. Saídas

`HorseExploration`, contendo:

- sementes utilizadas;
- caminhos candidatos;
- relações percorridas;
- pontuação estrutural de exploração;
- fronteira de nós alcançados;
- proveniência e avisos epistemológicos.

## 4. Regras arquiteturais

Horse:

- explora estruturas existentes;
- pode atravessar caminhos não lineares do grafo;
- pode usar PARSI para localizar sementes semanticamente relacionadas;
- pode usar StarHouse para orientar a fronteira estrutural;
- não cria conhecimento;
- não valida evidências;
- não afirma que uma conexão candidata seja verdadeira;
- não altera diretamente o `KnowledgeGraph`.

A pontuação produzida pelo módulo mede apenas **interesse estrutural da rota**, não probabilidade de verdade científica.

## 5. Critérios de aceite

1. Receber grafo válido.
2. Aceitar sementes explícitas e/ou resultado PARSI.
3. Explorar caminhos até profundidade configurável.
4. Priorizar rotas com diversidade estrutural/interdisciplinar.
5. Produzir resultado serializável e rastreável.
6. Não alterar o grafo.
7. Declarar que validação científica não foi realizada.
8. Expor `health_check()` e `stats()`.

## 6. Limites

Horse produz **candidatos de exploração**. Uma rota não constitui hipótese, evidência, descoberta ou previsão. A avaliação posterior pertence às camadas responsáveis por descoberta, validação, previsão e simulação.
