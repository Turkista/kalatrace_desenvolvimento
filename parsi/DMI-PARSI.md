# DMI-PARSI — Data & Module Interface

**Versão:** 1.0.0  
**Status:** Implementado  
**Camada:** Arquitetura Cognitiva  
**Tipo:** Núcleo Cognitivo  

## 1. Objetivo

PARSI é o primeiro estágio cognitivo do KALATRACE. Sua função é transformar
entrada textual bruta em uma representação semântica estruturada para os
módulos seguintes.

PARSI **não** valida evidência, não calcula verdade científica, não cria
hipóteses e não altera diretamente o Knowledge Graph.

## 2. Entrada

`PARSIEngine.interpret()` aceita:

- `str` com a informação bruta; ou
- `Mapping` contendo `statement`, `text`, `content`, `query` ou `description`.

Metadados opcionais podem ser fornecidos como `metadata` e uma origem em
`source`.

## 3. Saída

`PARSIResult` contém:

- `interpretation_id` — identificador rastreável;
- `raw_text` e `normalized_text`;
- `intent` — observation, question, hypothesis, experiment, evidence ou definition;
- `summary`;
- `entities` — candidatos semânticos;
- `relations` — relações explícitas detectadas no texto;
- `context` — idioma, modalidade, polaridade, marcadores temporais, domínio e fonte;
- `interpretation_confidence` — confiança **da interpretação estrutural**, não da verdade;
- `warnings`;
- `provenance` — módulo, versão, origem e declaração de que validação científica não ocorreu.

## 4. Critérios de aceite

1. Entrada vazia deve ser rejeitada.
2. A mesma entrada deve produzir uma representação determinística quanto às
   estruturas extraídas, exceto pelo `interpretation_id`.
3. A interpretação não pode alterar o grafo.
4. `interpretation_confidence` deve permanecer entre 0 e 1.
5. Linguagem assertiva não pode ser convertida automaticamente em verdade.
6. Relações devem ser registradas como **candidatas semânticas**.
7. O resultado deve ser serializável por `to_dict()`.
8. O módulo deve funcionar sem dependência de serviço externo de IA.

## 5. Integração com o Cognitive Orchestrator

No ciclo cognitivo, PARSI é executado imediatamente antes da criação da IEC.
O resultado é anexado aos metadados da IEC e retornado no resultado do ciclo.
A afirmação original permanece preservada para rastreabilidade.

## 6. Limites

A versão 1.0.0 usa heurísticas determinísticas de linguagem. Não deve ser
interpretada como NLP clínico, validação científica ou modelo de compreensão
semântica de propósito geral.

## 7. Próximo consumidor

O próximo módulo planejado é **StarHouse**, que poderá consumir a estrutura
semântica já produzida por PARSI junto ao Knowledge Graph e aos registries.
