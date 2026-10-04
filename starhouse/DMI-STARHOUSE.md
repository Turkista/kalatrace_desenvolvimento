# DMI — STARHOUSE

**Versão:** 1.0.0  
**Camada:** Arquitetura Cognitiva  
**Tipo:** Núcleo Cognitivo  
**Status:** Implementado

## 1. Finalidade

StarHouse é o observatório e a cartografia do universo de conhecimento do KALATRACE. Sua função é **observar, mapear e representar** estruturas existentes.

## 2. Entradas

- `KnowledgeGraph` e seus nós/arestas;
- domínio/tipo dos nós;
- relações e respectivos níveis de confiança já registrados.

## 3. Saídas

`StarHouseMap`, contendo:

- regiões de conhecimento;
- conexões observadas;
- nós isolados;
- conexões de baixa confiança;
- lacunas estruturais observadas;
- proveniência da observação.

## 4. Regras arquiteturais

StarHouse:

- observa e representa;
- não cria hipóteses;
- não valida evidências;
- não avalia verdade científica;
- não altera diretamente o conhecimento;
- não substitui a camada epistemológica.

Toda observação é uma fotografia estrutural do grafo no momento da execução.

## 5. Critérios de aceite

1. Receber um `KnowledgeGraph` válido.
2. Produzir mapa serializável.
3. Agrupar nós por domínio/tipo disponível.
4. Representar as conexões existentes sem reinterpretá-las.
5. Identificar nós isolados.
6. Identificar conexões abaixo do limiar de confiança do `KnowledgeGraph`.
7. Registrar que avaliação de verdade científica não foi realizada.
8. Não alterar o grafo recebido.
9. Expor `health_check()` e `stats()`.

## 6. Limites

As lacunas produzidas por StarHouse são **lacunas estruturais observadas**, não afirmações de que exista uma lacuna científica real. A interpretação investigativa posterior pertence aos módulos responsáveis por exploração, descoberta, previsão e estratégia.
