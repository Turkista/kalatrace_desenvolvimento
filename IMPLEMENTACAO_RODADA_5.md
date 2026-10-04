# KALATRACE v7 — Planner, Evolution Governance, Persistence Sync e Workspace Admin

## Implementado

1. **Planner/Coding Agent governado**
   - `core/agent_planning/coding_planner.py`
   - plano explícito com risco, etapas, validações e `execution_spec`.
   - planner nunca aprova nem executa alterações.

2. **Cognitive Cycle → Mission → Agent Task**
   - `core/evolution_pipeline/governed_cycle.py`
   - `POST /cmc/missions/{mission_id}/evolve`
   - opcionalmente executa o Cognitive Cycle, persiste IEC, sincroniza Neo4j e cria uma tarefa `coding_plan` em estado `planning`.
   - timeline CMC registra `agent_plan_proposed`.

3. **Código → testes → rollback**
   - preservada a execução controlada da v6.
   - tarefas de planejamento não entram automaticamente na fila executável; somente uma especificação explícita de `code_apply` pode chegar à aprovação.

4. **Persistência Supabase ↔ Neo4j**
   - `POST /persistence/sync/iec/{iec_id}` sincroniza uma IEC persistida no Supabase com `IEC` + `KnowledgeNode` no Neo4j.
   - ledger `knowledge_sync_status` registra `pending/synced/failed`, tentativas e erro.
   - `IEC` e `KnowledgeNode` permanecem entidades distintas.

5. **Administração de membros**
   - alteração de role via RPC protegido.
   - remoção de membro via endpoint protegido por RLS.
   - política de atualização impede elevação de privilégio pelo próprio membro.

6. **Auditoria de integração**
   - `scripts/audit_api_frontend.py`
   - `AUDITORIA_INTEGRACAO_v7.md` lista 113 rotas descobertas e informa que o frontend atual (`index.html`) não contém chamadas `fetch/axios` detectáveis estaticamente; portanto, a integração frontend ainda precisa de instrumentação/implementação real das telas.

## Validação

- `499 passed`
- `compileall` OK
- validação de sintaxe/import da aplicação ficou limitada neste ambiente porque o pacote Python `neo4j` não está instalado no runtime de auditoria; o `requirements.txt` do projeto já declara a dependência.

## Próximo bloco técnico

O próximo passo é conectar um provider LLM real ao contrato `CodingPlanner`, mantendo:

`LLM → plano explícito → aprovação → Local Agent → testes → evidência → validação → evolução`.

As credenciais de provedor devem permanecer exclusivamente no backend/local agent, nunca no frontend.
