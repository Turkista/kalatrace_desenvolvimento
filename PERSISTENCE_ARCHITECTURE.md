# KALATRACE — Persistência e fronteiras de dados

## Decisão arquitetural

- **Supabase/PostgreSQL** é a fonte transacional de verdade: Auth, IECs, evidências, previsões, simulações e registros brutos dos formulários de pesquisa.
- **Neo4j Aura** é a projeção persistente do Knowledge Graph: `KnowledgeNode` e `KnowledgeEdge`, além das entidades `IEC` e da relação `(:IEC)-[:REPRESENTS]->(:KnowledgeNode)`.
- **A API KALATRACE** é a camada de comunicação/orquestração entre os dois bancos. Não é necessário nem desejável criar uma conexão direta PostgreSQL → Neo4j para o fluxo normal.
- Um registro de formulário só vira parte do grafo quando houver uma razão semântica explícita. O dado bruto permanece no PostgreSQL.

## IEC × KnowledgeNode

`IEC` é uma unidade epistemológica/comparativa.

`KnowledgeNode` é uma unidade estrutural do grafo.

Uma IEC pode originar/representar um KnowledgeNode, mas os objetos são distintos e possuem IDs distintos.

## Formulários do MEDIKALAT

Os oito formulários da interface são persistidos em `research_form_records`, com auditoria em `research_form_record_events`:

- lote
- dose
- celular
- bruta
- toxico
- clinica
- naoconf
- relatorio

O campo `data` usa JSONB para preservar a estrutura dinâmica dos formulários sem bloquear a evolução da pesquisa. Os vínculos opcionais `iec_id` e `knowledge_node_id` permitem promover um registro ao contexto epistemológico/grafo quando apropriado.
