# KALATRACE — Rodada 3: Executor seguro, lifecycle CMC e integração operacional

## Implementado

### Agente Local — execução segura
- Criado `local_agent/sandbox.py`.
- Executor explícito e allowlisted, sem `shell=True` e sem execução de strings arbitrárias.
- Operações disponíveis: `pytest`, `compileall` e `node_check`.
- Validação de paths para impedir escape do workspace.
- Timeout configurável via `LocalAgentSandbox`.
- Remoção de variáveis de segredo sensíveis do ambiente do subprocesso.
- `LocalAgentRunner` agora pode executar `execution_spec` usando o sandbox quando nenhum handler customizado for fornecido.
- O runner anuncia a capability `sandbox_execution`.

### Fila do Agente Local
- `local_agent_tasks.execution_spec` persistido.
- Campos de governança: `claimed_by`, `approved_by`, `approved_at`, `execution_log`.
- `agent/status` deixa de reportar `not_connected` de forma fixa: consulta instâncias online/busy.
- Claim da próxima tarefa passou a usar função PostgreSQL com `FOR UPDATE SKIP LOCKED`, evitando que dois agentes reivindiquem a mesma tarefa.

### CMC
- Adicionado endpoint `/cmc/missions/{mission_id}/transition`.
- Transições continuam validadas pela `MissionStateMachine`.
- Mudança de estado é persistida em `cmc_missions`.
- Cada transição gera evento durável em `cmc_events`.
- A missão mantém a mesma identidade entre runtime e persistência.

### Projects
- Corrigida a incompatibilidade entre `project_templates` com `project_type=custom` e o antigo CHECK de `projects`.
- A migration passa a permitir tipos genéricos (`custom`, `simulation`, `research`, `ai`) além dos tipos existentes.

### Frontend
- Criação de tarefa do Agente Local agora pode declarar uma operação segura e um alvo.
- O painel continua permitindo tarefas apenas de planejamento quando nenhuma operação é selecionada.

## Validação
- `python -m pytest -q`: **490 passed**.
- `python -m py_compile`: OK para API, integração Supabase e Local Agent.
- Sandbox testado para operação permitida, operação arbitrária e path traversal.

## Ainda pendente

1. Executor cognitivo de coding completo: o sandbox atual executa somente operações de validação/teste; não gera ou modifica código autonomamente.
2. Integração E2E real com Supabase/Neo4j: depende das credenciais/configuração locais e de aplicar as migrations no projeto Supabase.
3. Auditoria endpoint-by-endpoint completa das Engines e do Cognitive Cycle ainda deve ser feita sobre execução real, não apenas análise estática.
4. Administração de usuários do Supabase Auth continua usando o modelo seguro de login + convite; operações administrativas que exigiriam service-role não foram adicionadas.
5. CMC ainda pode ganhar persistência automática de timeline completa além dos eventos de transição.

## Segurança / credenciais
Nenhuma credencial real foi adicionada. O sistema continua usando `.env` local e `.env.example` como documentação das variáveis necessárias.
