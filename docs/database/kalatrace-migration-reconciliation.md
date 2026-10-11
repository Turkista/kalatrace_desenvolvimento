# KALATRACE — reconciliação do histórico de migrações

**Data da auditoria:** 2026-10-11  
**Repositório:** `Turkista/kalatrace_desenvolvimento`  
**Base da PR:** `8056d114ce469e1e6d7f6a3c1cae601ec32c185f`  
**Projeto Supabase:** `kedyzontvnailtwpacvz`

## Resultado atual

- A pasta ativa `supabase/migrations/` tem **23 arquivos**.
- O histórico remoto `supabase_migrations.schema_migrations` tem **23 versões**.
- A comparação exata dos prefixos de versão encontrou **zero versões sem arquivo local e zero arquivos ativos sem versão remota**.
- Foram aplicadas sete migrações de workspace/CMC/agentes que já estavam versionadas no repositório, mas não estavam no banco. Como as versões antigas não existiam no histórico remoto, foram registradas sob novas versões de execução, de `20261011160607` a `20261011160830`.
- Os SQLs originais dessas sete migrações foram preservados em `_archive/supabase_migrations_original/`. Os arquivos ativos contêm as correções de segurança aplicadas.
- As migrações iniciais e de infraestrutura cujo SQL original não foi encontrado no histórico Git foram reconstruídas a partir do catálogo remoto. Os cabeçalhos dos arquivos identificam essas reconstruções; elas **não são apresentadas como cópias byte a byte dos originais**.
- O antigo `20261005_epistemic_evidence_relations.sql` foi retirado da pasta ativa e preservado em `_archive/supabase_migrations/`: essa versão não estava registrada remotamente e sua ordenação podia fazê-la executar antes da criação da tabela `evidence`.
- O arquivo antigo `20261008170000_add_infrastructure_usage_rpc.sql`, que não correspondia à versão aplicada e poderia sobrescrever uma RPC mais nova em um `db push`, foi substituído pelo baseline reconstruído na versão remota `20261008190604`.

## Correções de segurança aplicadas

### Watchdog de infraestrutura

Migração remota: `20261011153829_harden_infrastructure_watchdog_admin_access.sql`.

- Criada allowlist privada de administradores de infraestrutura, com o administrador inicial deste projeto.
- Leitura de snapshots, eventos e verificações de runtime restrita a administradores.
- RPCs de consulta, execução e registro do Watchdog verificam a autorização administrativa.
- As RPCs privilegiadas usam `SECURITY DEFINER` com `search_path` vazio e não podem ser executadas por `anon`.
- Não foram concedidos privilégios diretos de UPDATE/DELETE a `authenticated` nas tabelas do Watchdog.
- Teste SQL com claims simulados: o administrador inicial consultou as métricas e um UID não autorizado foi bloqueado nas três RPCs. Isso não equivale a um teste end-to-end por PostgREST.

### Perfil e papel de usuário

Migração remota: `20261011154847_harden_profile_role_update_privileges.sql`.

A política de atualização do próprio perfil, combinada com UPDATE de tabela inteira, permitia tentativa de alterar `profiles.role`. Agora `authenticated` não possui UPDATE de tabela nem UPDATE da coluna `role`; mantém apenas UPDATE em `display_name`. A verificação de privilégios no catálogo confirmou esse resultado.

### Workspace, membros e projetos

Migrações remotas:
- `20261011160607_workspace_projects_cmc_reconciled`
- `20261011160639_workspace_templates_cmc_agent_hardened`
- `20261011160659_agent_sandbox_cmc_lifecycle_hardened`
- `20261011160719_agent_coding_cmc_timeline_hardened`
- `20261011160752_cognitive_agent_governance_hardened`
- `20261011160811_knowledge_sync_outbox`
- `20261011160830_workspace_member_admin_hardened`

Correções incluídas antes da aplicação:
- membros não podem alterar o próprio papel por UPDATE direto;
- mudanças de papel passam pela RPC autorizada, e UPDATE direto em `project_memberships` foi revogado;
- usuários autenticados só podem atualizar campos de negócio do projeto, não `owner_id`, `slug` ou IDs;
- a função `can_manage_project` valida o usuário da sessão atual e usa `search_path` vazio;
- funções de convite e timeline usam `search_path` vazio;
- convites só são aceitos quando o e-mail do usuário está confirmado, e um convite não sobrescreve o papel de uma associação já existente;
- instâncias de agente são visíveis apenas ao proprietário;
- a função de claim verifica a propriedade da instância e limita membros autorizados a executar tarefas;
- o campo `owner_id` de tarefas não pode ser alterado, tarefas não podem começar já aprovadas, somente papéis autorizados podem aprovar e a especificação de execução fica imutável após aprovação.

Migração adicional:
- `20261011161017_guard_agent_task_insert_approval.sql` fecha explicitamente o caminho de inserir tarefas já aprovadas.

Verificações no catálogo confirmaram as tabelas, RLS, funções, políticas, grants e o trigger `BEFORE INSERT OR UPDATE` de tarefas. Um teste SQL anterior à correção adicional de INSERT confirmou o bloqueio de aprovação por usuário não autorizado, a transição direta de `queued` para `running` e a alteração da especificação após aprovação. A correção posterior de INSERT foi verificada no catálogo; o teste end-to-end completo continua pendente.

## Migrações reconstruídas

As seguintes versões estavam registradas no Supabase, mas seus SQLs originais não foram encontrados no histórico Git verificado:

- `20260824171006_initial_kalatrace_auth_and_knowledge_schema`
- `20260824171611_harden_kalatrace_rls_data_api_access`
- `20260824234247_harden_public_security_definer_and_index_iec_nodes`
- `20261008190604_add_infrastructure_usage_rpc`
- `20261008191018_extend_infrastructure_health_rpc`

Os arquivos locais foram reconstruídos a partir das colunas, constraints, índices, políticas, triggers e definições de funções encontradas no banco. Eles permitem avançar para um reset local reproduzível, mas ainda precisam ser validados num ambiente local limpo. Não se deve afirmar que são os SQLs originais.

Os nomes divergentes de formulários e projetos foram alinhados aos prefixos já registrados no banco:
- `20260827172835_add_research_form_records_and_links.sql`
- `20260827174829_add_projects_and_local_agent_control.sql`

## Pendências reais

1. Executar um reset local limpo e confirmar que os 23 arquivos recriam o schema sem dependências ausentes ou divergências inesperadas.
2. Fazer teste end-to-end via PostgREST com duas sessões autenticadas diferentes, incluindo leitura/alteração cruzada, convite de membro, mudança de papel e aprovação de tarefa.
3. Habilitar a proteção de senha comprometida no dashboard de Auth do Supabase.
4. Reexecutar os advisors depois da rodada de migrações.
5. Revisar os índices que o advisor classifica como não utilizados; não removê-los apenas com base nesse alerta.

O login de `index.html` não foi alterado nesta etapa.
