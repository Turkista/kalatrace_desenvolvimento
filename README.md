# KALATRACE

<p align="center">
  <h3 align="center">Sistema Operacional para Construção do Conhecimento Científico</h3>
  <p align="center">
    Uma plataforma para organizar, validar, rastrear e evoluir o conhecimento científico de forma explicável, auditável e reproduzível.
  </p>
</p>

---

## Visão Geral

O **KALATRACE** é uma plataforma desenvolvida para apoiar pesquisadores na construção e evolução do conhecimento científico.

Diferentemente de aplicações tradicionais baseadas em Inteligência Artificial, o KALATRACE **não utiliza modelos de IA como fonte de verdade**.

Os modelos de IA atuam apenas como colaboradores especializados. Toda a governança científica permanece sob responsabilidade da arquitetura do próprio KALATRACE.

Seu objetivo é permitir que hipóteses, evidências, mecanismos biológicos, experimentos, inferências e descobertas sejam construídos de forma organizada, rastreável e continuamente evolutiva.

---

# Missão

Construir uma plataforma capaz de integrar pesquisadores, conhecimento científico e Inteligências Artificiais em uma única arquitetura de pesquisa, preservando rastreabilidade, transparência e qualidade científica.

---

# Visão

Ser uma plataforma de referência para pesquisa científica assistida por Inteligência Artificial, onde todo conhecimento produzido seja:

- Explicável
- Auditável
- Reproduzível
- Evolutivo
- Independente de qualquer fornecedor de IA

---

# Filosofia

O KALATRACE foi construído sobre cinco princípios fundamentais.

## Conhecimento acima da IA

A Inteligência Artificial não substitui o pesquisador.

Ela apenas auxilia determinadas etapas do processo científico.

O conhecimento permanece sob controle da arquitetura do KALATRACE.

---

## Rastreabilidade

Toda conclusão deve possuir origem conhecida.

Cada hipótese pode ser rastreada até suas evidências.

Cada inferência possui histórico completo.

---

## Explicabilidade

Nenhuma conclusão existe sem explicação.

Todo raciocínio produzido pelo sistema pode ser reconstruído posteriormente.

---

## Evolução Contínua

O conhecimento científico nunca é considerado definitivo.

Cada objeto científico pode evoluir preservando seu histórico.

---

## Arquitetura Modular

Todos os componentes do sistema são independentes.

Isso permite evolução contínua sem comprometer a arquitetura.

---

# O que torna o KALATRACE diferente?

A maioria das aplicações utiliza Inteligência Artificial para responder perguntas.

O KALATRACE foi projetado para **construir conhecimento científico**.

Em vez de apenas gerar respostas, ele organiza:

- perguntas científicas;
- hipóteses;
- evidências;
- mecanismos;
- experimentos;
- inferências;
- descobertas;
- histórico de raciocínio.

O resultado é uma plataforma que preserva toda a cadeia de construção do conhecimento.

---

# Arquitetura Geral

Fluxo oficial de execução, conforme o Documento T1 (Especificação Técnica da Arquitetura):

```
                 Pesquisador
                      │
                     API
                      │
                    Core
                      │
            Cognitive Orchestrator
                      │
                  Engine(s)
                      │
                 Knowledge
                      │
                    Graph
                      │
                 Governance
                      │
                  Storage
                      │
                  Resposta
```

> A "Camada de Serviços" citada em versões anteriores deste README pertence a uma
> revisão posterior da arquitetura (Documento 71 — Architecture Freeze), que ainda
> **não foi adotada** neste repositório. A implementação atual segue o Blueprint
> original (Documentos T1–T3), sem uma camada Service separada — ver seção
> "Estrutura Atual do Projeto" abaixo.

---

# Núcleo Cognitivo

O núcleo do KALATRACE é formado por cinco componentes fundamentais.

```
ScientificObject

↓

IEC (Intelligent Evidence Component)

↓

Knowledge Graph

↓

Knowledge Service

↓

Reasoning Trace
```

Toda a plataforma é construída sobre esse núcleo.

---

# Componentes Principais

## Scientific Objects

Representam todas as entidades científicas do sistema.

Já implementados em `knowledge/`:

- IEC
- Evidence
- Hypothesis
- Discovery
- Concept
- Relationship
- Scientific Question

Previstos, ainda não implementados:

- Experiment
- Mechanism
- Insight
- Simulation
- Scientific Report

---

## Knowledge Graph

Responsável por representar toda a rede de conhecimento científico.

Inclui:

- relações
- evidências
- mecanismos
- proveniência
- histórico
- contexto

Implementado em `graph/` (`knowledge_graph.py` e `discovery_graph/`).

---

## Engines Cognitivos

Executam processamento científico especializado. Vivem em `engine/`, conforme o
Documento T3 (Especificação Técnica do Framework de Engines):

- Scientific Research Engine
- Reasoning Engine
- Curiosity Engine
- Scientific Context Engine
- Knowledge Evolution Engine
- Research Strategy Engine
- Cognitive Orchestrator

> O **Validation Engine** não faz parte desta lista porque, segundo o Documento T3,
> Validação é uma camada própria (`validation/`), e não um Engine. Ele vive em
> `validation/validation_engine.py`.

Strategy Engine e Simulation Engine ainda não têm implementação própria — hoje
`research_strategy/` cobre parte do papel de Strategy, e Simulation ainda não existe.

---

## Sistema Multiagente

Coordena os Engines durante uma investigação científica. Vive em `agents/`.

Agentes previstos:

- ResearchAgent ✅
- ReasoningAgent ✅
- ValidationAgent ✅
- CuriosityAgent ✅
- OrchestratorAgent ✅
- StrategyAgent — ainda não implementado
- SimulationAgent — ainda não implementado

---

## Camada de Serviços

**Status: não implementada.**

Essa camada (`KnowledgeService`, `EvidenceService`, `OntologyService`, `AuditService`,
`ProjectService`) foi definida em uma revisão posterior da arquitetura (Documento 71),
que introduziu um modelo de 7 camadas com Service entre Engine e Knowledge.

O backend atual segue o Blueprint original (T1–T3), onde a comunicação entre Engine,
Knowledge e Storage acontece sem uma camada Service intermediária. A pasta `services/`
existe no repositório apenas como reserva de espaço, sem conteúdo.

Se o projeto decidir adotar o Documento 71 no futuro, essa camada precisará ser
implementada e o fluxo de execução acima revisado — isso deve ser tratado como uma
decisão arquitetural formal, não uma alteração informal.

---

# Estrutura Atual do Projeto

Estrutura alinhada ao Blueprint Arquitetural (Documentos T1–T3).

```
kalatrace_backend/

├── core/                     # Infraestrutura central (T2)
│   ├── __init__.py
│   ├── constants.py
│   ├── event_bus.py
│   ├── exceptions.py
│   ├── lifecycle_manager.py
│   ├── logger.py
│   ├── registry.py
│   └── orchestrator/         # dispatcher, engine, execution_context, pipeline, scheduler, workflow
│
├── engine/                    # Motores cognitivos (T3) — nome singular conforme spec
│   ├── base/
│   ├── curiosity/
│   ├── reasoning/
│   ├── scientific_research/
│   ├── scientific_context/
│   ├── knowledge_evolution/
│   ├── research_strategy/
│   └── cognitive_orchestrator/
│
├── knowledge/                 # IEC, Evidence, Hypothesis, Discovery, Concept, Relationship, Ontology
├── graph/                     # Knowledge Graph e Discovery Graph
├── governance/                 # Confidence, Audit, Version, Provenance, Event
├── validation/                 # Validação estrutural e epistemológica (inclui validation_engine.py)
├── storage/                    # Persistência (inclui evidence_store.py)
├── memory/                     # Working, Episodic, Semantic memory + insight registry
├── curation/                   # Normalização e curadoria de dados científicos
├── evolution/                   # Histórico evolutivo do conhecimento
├── inference/                   # Modelos formais de inferência
├── metacognition/                # Autoavaliação, automonitoramento, autorreflexão
├── acquisition/                  # Aquisição de conhecimento externo
├── agents/                       # Sistema multiagente
├── registries/                    # Registros específicos de domínio (evidence, hypothesis, insight)
├── api/                            # Camada de comunicação externa (FastAPI)
├── config/                         # Configurações e settings
├── utils/                          # Ferramentas auxiliares
├── services/                       # Reservado — não implementado (ver seção "Camada de Serviços")
├── infrastructure/, models/, ontology/, persistence/, shared/, tests/, docs/
│
├── app.py
├── run.py
├── requirements.txt
└── README.md
```

> **Nota de reorganização:** `events/` e `orchestration/` (pastas soltas na raiz)
> foram removidas — seu conteúdo foi consolidado dentro de `core/`, conforme a
> Especificação Técnica do Core (Documento T2). `engines/` foi renomeado para
> `engine/` (singular) para bater com a Especificação Técnica do Framework de
> Engines (Documento T3). As duas implementações duplicadas de `ValidationEngine`
> (`validation/` e a antiga `engines/validation/`) e de `EvidenceStore`
> (`storage/` e `memory/`) foram consolidadas em uma única versão cada, mantida
> no local correto segundo a spec.

**Estado de implementação:** dos 211 arquivos `.py` do backend, 27 têm código
real implementado; o restante são placeholders vazios criados para preservar a
estrutura oficial antes da implementação. Os módulos mais maduros hoje são
`curation/curation.py`, `core/lifecycle_manager.py`, `graph/knowledge_graph.py`,
`engine/reasoning/engine.py`, `validation/validation_engine.py`,
`storage/evidence_store.py` e `api/api.py`.

---

# Tecnologias

Backend

- Python
- FastAPI
- Pydantic

Banco de Dados

- Neo4j
- PostgreSQL

Infraestrutura

- Docker
- Docker Compose

Testes

- Pytest

Documentação

- MkDocs
- OpenAPI

---

# Integração com Inteligências Artificiais

O KALATRACE foi desenvolvido para ser independente de qualquer fornecedor de IA.

A arquitetura permitirá integração com diferentes provedores, como:

- OpenAI
- Anthropic
- Google Gemini
- DeepSeek
- Mistral
- Llama
- Qwen
- Outros modelos open source

Esses modelos são utilizados apenas como mecanismos de apoio.

Toda a validação, rastreabilidade, governança e evolução do conhecimento permanecem sob responsabilidade do próprio KALATRACE.

Por decisão de projeto, a classificação epistemológica (escalas E0–E5 e S0–S5) é
feita manualmente — a integração de IA para essa etapa fica reservada para uma
fase futura, quando houver volume real de dados.

---

# Estado Atual do Projeto

**Fase de Desenvolvimento**

🟢 Arquitetura Científica concluída

🟢 Arquitetura Cognitiva concluída

🟢 Arquitetura de Engenharia concluída

🟢 Modelo de Domínio definido

🟢 Contratos de Engenharia definidos

🟢 Roadmap de Desenvolvimento concluído

🟢 Blueprint de Execução concluído

🟢 Esqueleto de pastas reorganizado e validado contra o Blueprint T1–T3

🟡 Implementação do Kernel Cognitivo em andamento (`core/`, `knowledge/`, `graph/` parcialmente implementados)

🔴 Camada de Serviços — não iniciada (decisão pendente sobre adotar ou não o Documento 71)

---

# Roadmap

## Fase 1

Infraestrutura da Plataforma

---

## Fase 2

Modelo de Domínio

---

## Fase 3

Persistência

---

## Fase 4

Camada de Serviços *(pendente de decisão arquitetural — ver seção "Camada de Serviços")*

---

## Fase 5

Engines Cognitivos

---

## Fase 6

Sistema Multiagente

---

## Fase 7

API

---

## Fase 8

Interface Científica

---

## Fase 9

Integração com o MEDIKALAT

---

## Fase 10

Validação Científica

---

# Filosofia de Desenvolvimento

Todo desenvolvimento do KALATRACE segue quatro princípios permanentes:

- Arquitetura antes da implementação.
- Desenvolvimento incremental.
- Desenvolvimento vertical (funcionalidades completas).
- Testes desde o primeiro componente.

Estratégia vertical adotada: **Core → Knowledge/IEC → Graph → Governance → Storage**,
conectada a dados reais (Google Sheets) antes de expandir para os demais módulos.

---

# Documentação

A documentação do projeto está organizada nas seguintes etapas:

- Fundação Científica (Documentos T1–T41 — Blueprint Arquitetural)
- Arquitetura Cognitiva (Documentos 42–60 — Componentes Cognitivos)
- Arquitetura de Engenharia (Documentos 61–72 — Especificação Técnica e Implementação)
- Planejamento de Desenvolvimento
- Manual de Engenharia

---

# Objetivo de Longo Prazo

O KALATRACE não pretende ser apenas mais uma aplicação de Inteligência Artificial.

Seu objetivo é tornar-se um **Sistema Operacional para Construção do Conhecimento Científico**, capaz de integrar pesquisadores, Inteligências Artificiais, evidências experimentais e conhecimento científico em uma arquitetura única, transparente e evolutiva.

---

# Licença

Em definição.

---

# Autor

**Projeto KALATRACE**

Sistema Operacional para Construção do Conhecimento Científico

*"Construindo conhecimento científico com rastreabilidade, explicabilidade e evolução contínua."*

---

# Arquitetura Cognitiva — Fase 5

A implementação da nova camada cognitiva está sendo executada **um módulo por vez**, com testes e integração antes da passagem ao próximo:

**PARSI → StarHouse → Horse → Prediction → Simulation**

### Estado atual

- **PARSI — IMPLEMENTADO v1.0.0**: primeiro estágio cognitivo; interpreta entradas brutas e produz representação semântica estruturada sem validar verdade científica.
- **StarHouse — IMPLEMENTADO v1.0.0**: observatório e cartografia do conhecimento existente.
- **Horse — IMPLEMENTADO v1.0.0**: exploração cognitiva não linear de caminhos existentes.
- **Prediction — IMPLEMENTADO v1.0.0**: projeção probabilística de tendências e cenários, com pressupostos, incerteza e proveniência.
- **Simulation — PENDENTE**: laboratório virtual de cenários.

O contrato de implementação do PARSI está em `parsi/DMI-PARSI.md` e o roadmap atualizado está em `docs/KALATRACE_Roadmap_Fase5_PARSI_atualizado.docx`.

O contrato de implementação do StarHouse está em `starhouse/DMI-STARHOUSE.md`. O StarHouse v1.0.0 observa e cartografa o KnowledgeGraph sem validar verdade científica ou modificar o conhecimento. A implementação atualizada está no roadmap `docs/KALATRACE_Roadmap_Fase5_STARHOUSE_atualizado.docx`.

O contrato de implementação do Horse está em `horse/DMI-HORSE.md`. O Horse v1.0.0 explora caminhos não lineares e conexões candidatas sem criar conhecimento, validar evidências ou modificar o grafo. A implementação atualizada está no roadmap `docs/KALATRACE_Roadmap_Fase5_HORSE_atualizado.docx`.

### Prediction — IMPLEMENTADO v1.0.0
Prediction agora projeta cenários probabilísticos a partir de sinais observáveis do KnowledgeGraph, StarHouse e Horse, preservando pressupostos, incerteza e proveniência. Não valida evidências, não estabelece causalidade e não modifica o conhecimento.

O contrato de implementação está em `prediction/DMI-PREDICTION.md`.
