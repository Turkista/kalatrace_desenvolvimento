# PARSI

## Função Arquitetural

PARSI representa a capacidade de compreensão e interpretação do KALATRACE.

## Responsabilidade

Interpretar informações recebidas pelo sistema, extraindo significado,
contexto e estrutura semântica para os módulos seguintes.

## Categoria

Camada: Arquitetura Cognitiva  
Tipo: Núcleo Cognitivo

## Papel no Sistema

PARSI atua como o primeiro estágio cognitivo do KALATRACE, transformando dados
e informações brutas em uma representação semântica estruturada.

A implementação 1.0.0 é determinística e local: normaliza texto, classifica a
intenção, identifica sinais de modalidade/polaridade, extrai entidades e
relações candidatas e organiza contexto/proveniência.

## Comunicação

Recebe informações de:

- API
- Engines
- Serviços de entrada de dados
- Cognitive Orchestrator

Comunica-se principalmente com:

- Knowledge
- Graph
- Cognitive Orchestrator

## Limitações

PARSI não valida conhecimento científico, não atribui verdade a afirmações,
não cria hipóteses e não altera o Knowledge Graph diretamente.

A validação pertence à camada epistemológica.

## Status

**IMPLEMENTADO — v1.0.0**

Ver `DMI-PARSI.md` para o contrato de entrada/saída e critérios de aceite.
