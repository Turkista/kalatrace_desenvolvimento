# KALATRACE — Supabase + Neo4j

## Responsabilidades

| Componente | Responsabilidade |
|---|---|
| Supabase Auth | Identidade e sessões |
| Supabase PostgreSQL | Dados relacionais, RLS, IEC, Evidence, Predictions, Simulations |
| Neo4j Aura | Knowledge Graph persistente: KnowledgeNode/KnowledgeEdge |
| KALATRACE local | Engines, agentes, inferência, validação, simulação e API |

**Regra arquitetural:** KnowledgeNode e IEC são entidades distintas. IEC pode referenciar KnowledgeNodes, mas não é substituído por eles.
