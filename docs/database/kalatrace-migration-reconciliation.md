# KALATRACE — reconciliação do histórico de migrações

**Data da auditoria:** 2026-10-11  
**Repositório:** `Turkista/kalatrace_desenvolvimento`  
**Branch de referência:** `main`, commit-base `8056d114ce469e1e6d7f6a3c1cae601ec32c185f`  
**Projeto Supabase verificado:** `kedyzontvnailtwpacvz`

## Objetivo e limite de segurança

Este documento registra divergências observadas entre `supabase/migrations/` no GitHub, o histórico retornado pelo Supabase e os objetos do schema remoto. Não autoriza executar `db push`, reaplicar DDL ou alterar manualmente o histórico remoto.

A contagem de arquivos não prova, por si só, que existam migrações pendentes: nomes/versões podem ter sido renomeados, migrações podem ter sido aplicadas por outro caminho e módulos podem não fazer parte do banco ativo.

## Estado observado antes da nova correção

- GitHub em `main` no início da auditoria: 17 arquivos em `supabase/migrations/`.
- Supabase antes das correções desta rodada: 13 versões registradas no histórico remoto.
- Branch desta PR após as correções: 23 arquivos ativos de migração e 23 versões no histórico Supabase; a comparação exata dos prefixos de versão não encontrou migrações ausentes nem arquivos sem registro.
- As três migrações recentes de segurança/performance abaixo estavam presentes nos dois lados:
  - `20261011144046_revoke_unsafe_public_table_privileges`
  - `20261011144806_harden_trigger_function_search_path_and_index_task_owner`
  - `20261011144858_remove_redundant_research_form_select_policy`
- As tabelas `research_form_records`, `projects`, `local_agent_tasks`, `evidence`, `evidence_iec_links`, `evidence_history`, `iec_state_history` e `knowledge_evolution_events` existem no banco.
- Os módulos workspace/CMC possuem arquivos de migração, mas as tabelas correspondentes a `workspace_projects`, `workspace_templates`, `agent_sandbox`, `agent_coding_tasks`, `cognitive_agent_governance`, `knowledge_sync_outbox` e `workspace_members` não foram encontradas no catálogo consultado. Não aplicar esses módulos em lote sem revisar dependências, uso no código e políticas RLS.
- O histórico remoto registra `20261008191018 extend_infrastructure_health_rpc`, mas não há arquivo correspondente na pasta atual.
- A função pública `get_kalatrace_infrastructure_usage()` chama `private.collect_kalatrace_infrastructure_usage()`. A implementação versionada em `20261008170000_add_infrastructure_usage_rpc.sql` não corresponde à implementação remota, que coleta métricas adicionais e usa um wrapper com `search_path` vazio.
- `20261005_epistemic_evidence_relations.sql` continha DDL substancial, mas sua versão não estava registrada remotamente e seu prefixo faria com que fosse executada antes da criação de `evidence` em um reset limpo. Foi movida para `_archive/supabase_migrations/`; `20261007135705_epistemic_evidence_relations.sql` permanece como no-op versionado e o schema é criado por `20261007135646`.

## Matriz de divergências

| Versão/nome | Evidência no GitHub | Evidência remota | Classificação | Ação segura |
|---|---|---|---|---|
| `20260824171006 initial_kalatrace_auth_and_knowledge_schema` | Arquivo original não encontrado no histórico Git; foi adicionado arquivo reconstruído a partir do catálogo remoto | Versão registrada | Original ausente; baseline reconstruído | Validar em reset local limpo; não apresentar como cópia byte a byte do original |
| `20260824171611 harden_kalatrace_rls_data_api_access` | Original ausente; arquivo reconstruído a partir das políticas/grants atuais | Versão registrada | Baseline reconstruído | Validar event trigger e políticas em reset local limpo |
| `20260824234247 harden_public_security_definer_and_index_iec_nodes` | Original ausente; arquivo reconstruído com índice e função de trigger endurecida | Versão registrada | Baseline reconstruído | Validar em reset local limpo |
| Formulários de pesquisa | `20260827120000_add_research_form_records.sql` | `20260827172835 add_research_form_records_and_links` | Versão divergente | Comparar SQL completo, políticas e schema antes de escolher versão canônica |
| Projetos/agentes locais | `20260827130000_add_projects_and_local_agent_control.sql` | `20260827174829 add_projects_and_local_agent_control` | Versão divergente | Comparar SQL completo, políticas e schema antes de escolher versão canônica |
| Evidência/relacionamentos | `20261005_epistemic_evidence_relations.sql` e `20261007135705_epistemic_evidence_relations.sql` | Versão `20261007135705` registrada | Possível arquivo legado duplicado | Confirmar origem; remover/arquivar só em PR separada |
| Uso de infraestrutura | `20261008170000_add_infrastructure_usage_rpc.sql` | `20261008190604 add_infrastructure_usage_rpc` | Fonte divergente | Recuperar SQL aplicado; manter versão corrigida com privilégios e search_path explícitos |
| Saúde/runtime da infraestrutura | Arquivo reconstruído como `20261008191018_extend_infrastructure_health_rpc.sql` a partir das colunas, constraints, índices e definição remota da RPC | `20261008191018 extend_infrastructure_health_rpc` | Baseline reconstruído | Validar em reset local limpo; o original exato não foi recuperado |
| Workspace/CMC/agent governance | Sete migrações versionadas e endurecidas nesta branch, movidas para versões de execução atuais; fontes originais preservadas em `_archive/supabase_migrations_original/` | As tabelas de workspace, CMC, instâncias e sincronização agora existem | Aplicadas e reconciliadas | Testes end-to-end de autorização ainda pendentes |

## Achado adicional: exposição e execução das RPCs de infraestrutura

A consulta ao catálogo remoto confirmou:

1. As políticas de leitura de `infrastructure_usage_snapshots` e `infrastructure_watchdog_events` permitiam SELECT a qualquer usuário autenticado.
2. `get_kalatrace_infrastructure_usage()` e `run_kalatrace_watchdog()` eram wrappers de invocador (`SECURITY INVOKER`) que chamavam funções privadas sem privilégio EXECUTE concedido à role `authenticated`. A chamada direta pelo usuário autenticado podia falhar por permissão.
3. `record_kalatrace_watchdog_runtime()` tentava atualizar snapshots, mas `authenticated` não tinha UPDATE nas tabelas. A função também só verificava se havia usuário autenticado, não um papel administrativo.
4. A proteção por RLS não pode ser contornada concedendo UPDATE amplo à role `authenticated`; as rotinas precisam de autorização explícita e privilégios mínimos.
5. A tabela `profiles` permitia UPDATE no registro próprio e continha o campo `role` (`user`, `admin`, `agent`). O privilégio era de tabela inteira, então um usuário autenticado poderia tentar promover o próprio perfil por API direta.

### Correções implementadas nesta branch e no banco remoto

A migração `20261011153829_harden_infrastructure_watchdog_admin_access.sql` foi preparada para:

- criar uma allowlist privada de administradores de infraestrutura e registrar o administrador inicial já existente neste projeto;
- restringir as políticas RLS de snapshots, eventos e runtime checks a administradores;
- proteger as três RPCs com verificação de administrador, `SECURITY DEFINER` e `search_path` vazio;
- validar estados recebidos e rejeitar snapshot inexistente;
- manter revogados os privilégios diretos de escrita para usuários autenticados.

**Watchdog:** migração aplicada no projeto remoto e registrada como `20261011153829 harden_infrastructure_watchdog_admin_access`. A consulta ao catálogo confirmou as quatro RPCs com `SECURITY DEFINER`, `search_path` vazio, execução negada a `anon` e concedida a `authenticated`, com verificação administrativa dentro das funções. A allowlist contém o administrador inicial; os privilégios diretos de UPDATE/DELETE para `authenticated` continuam negados. Um teste SQL com claims simulados confirmou que o administrador inicial consegue consultar métricas e que um UID não autorizado é bloqueado nas três RPCs. **Perfis:** migração aplicada e registrada como `20261011154847 harden_profile_role_update_privileges`; verificação de privilégios confirmou que `authenticated` não possui UPDATE de tabela nem UPDATE da coluna `role`, mas mantém UPDATE em `display_name`.

**Workspace/CMC e agentes:** sete migrações foram aplicadas em sequência e registradas nas versões `20261011160607` a `20261011160830`. As políticas e funções foram endurecidas antes da aplicação: inserção de membros pelo fluxo de convite/owner, alteração de papéis via RPC autorizada, colunas de ownership de projetos sem UPDATE direto, instâncias de agente visíveis apenas ao proprietário, aprovação de tarefas protegida por papel e especificação de execução imutável após aprovação. A migração `20261011161017_guard_agent_task_insert_approval` fecha também o caminho de inserir tarefas já aprovadas.

**Reconciliação:** a consulta final encontrou 23 arquivos de migração ativos e 23 versões remotas, sem versões faltando de um lado ou do outro. As migrações iniciais e de infraestrutura sem SQL original no histórico Git foram reconstruídas a partir do catálogo remoto e marcadas explicitamente como reconstruções; as fontes originais das migrações workspace foram preservadas no diretório `_archive/`.

Essas verificações de catálogo e testes SQL não substituem um teste end-to-end por PostgREST com duas sessões reais.

## Sequência de reconciliação

1. Recuperar os três arquivos de migração iniciais e o arquivo de saúde/runtime a partir de histórico/backup confiável.
2. Obter o SQL exato das migrações registradas remotamente quando possível e comparar com as definições de funções, triggers, policies, grants, constraints, índices e colunas atuais.
3. Classificar cada versão como correspondente, renomeada, duplicada, não aplicada intencionalmente ou não resolvida.
4. Restaurar arquivos históricos sem executar SQL; alinhar nomes/versões só depois de validar a estratégia suportada pelo Supabase CLI.
5. Avaliar os módulos workspace/CMC em mudança isolada, com revisão de autorização/RLS e testes.
6. Planejar migrações novas apenas para diferenças de schema comprovadas. Não editar manualmente o histórico remoto e não reaplicar DDL especulativo.

## Verificações pendentes

- Validação dos arquivos reconstruídos em um reset local limpo. Os arquivos originais não foram encontrados no histórico Git; os novos arquivos são reconstruções explícitas baseadas no catálogo remoto, não cópias byte a byte.
- Confirmar por reset local que as migrações reconstruídas reproduzem o schema sem dependências ausentes.
- Teste end-to-end via PostgREST com duas sessões autenticadas reais, incluindo papéis diferentes e isolamento entre usuários.
- Teste RLS end-to-end com duas sessões autenticadas separadas.
- Habilitar proteção de senha comprometida nas configurações de Auth do Supabase.
- Revisar os 25 índices marcados como não utilizados; não removê-los apenas com base no advisor.
- Reexecutar advisors após a migração de segurança.

## Critério para encerrar

A reconciliação só estará concluída quando cada versão remota tiver uma fonte local confiável ou exceção documentada, cada diferença de schema tiver uma decisão registrada, as RPCs estiverem protegidas e funcionais, e a sequência de migração estiver validada sem reaplicar mudanças existentes.
