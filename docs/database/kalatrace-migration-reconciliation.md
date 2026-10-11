# KALATRACE — reconciliação do histórico de migrações

**Data da auditoria:** 2026-10-11  
**Repositório:** `Turkista/kalatrace_desenvolvimento`  
**Branch de referência:** `main` (auditoria iniciada após o commit `8056d114ce469e1e6d7f6a3c1cae601ec32c185f`)  
**Projeto Supabase verificado:** `kedyzontvnailtwpacvz`

## Objetivo e limite de segurança

Este documento registra divergências observadas entre `supabase/migrations/` no GitHub, o histórico retornado pelo Supabase e os objetos encontrados no schema remoto. Ele **não** autoriza executar `db push`, reaplicar DDL ou alterar manualmente o histórico remoto.

A contagem de arquivos não é, isoladamente, prova de migrações pendentes: nomes/versões podem ter sido renomeados, migrações podem ter sido aplicadas por outro caminho e alguns módulos podem não fazer parte do banco ativo.

## Estado observado

- GitHub: 17 arquivos em `supabase/migrations/`.
- Supabase: 13 versões registradas no histórico remoto.
- As três migrações recentes de segurança/performance abaixo estão presentes nos dois lados:
  - `20261011144046_revoke_unsafe_public_table_privileges`
  - `20261011144806_harden_trigger_function_search_path_and_index_task_owner`
  - `20261011144858_remove_redundant_research_form_select_policy`
- No schema remoto, `research_form_records`, `projects`, `local_agent_tasks`, `evidence`, `evidence_iec_links`, `evidence_history`, `iec_state_history` e `knowledge_evolution_events` existem.
- As tabelas de workspace/CMC listadas abaixo não foram encontradas no catálogo consultado: `project_memberships`, `cmc_missions`, `workspace_profiles`, `project_invitations`, `local_agent_instances`, `knowledge_sync_status`. Isso é evidência de ausência desses objetos com esses nomes no schema consultado, não prova de que todo o código associado deva ser implantado.
- A função pública `get_kalatrace_infrastructure_usage()` existe no banco e encaminha a coleta para `private.collect_kalatrace_infrastructure_usage()`. A versão do arquivo GitHub `20261008170000_add_infrastructure_usage_rpc.sql` contém uma implementação anterior/diferente.
- O histórico remoto contém `20261008191018 extend_infrastructure_health_rpc`, mas não foi localizado arquivo correspondente na pasta de migrações atual.
- `20261005_epistemic_evidence_relations.sql` contém DDL sobre evidências/relacionamentos, enquanto `20261007135705_epistemic_evidence_relations.sql` é um marcador no-op que declara o schema já representado pela migração persistente anterior. O arquivo de 2026-10-05 deve ser tratado como candidato a legado duplicado, não executado automaticamente.

## Matriz de divergências

| Versão/nome | Evidência no GitHub | Evidência remota | Classificação atual | Ação segura |
|---|---|---|---|---|
| `20260824171006 initial_kalatrace_auth_and_knowledge_schema` | Arquivo com essa versão não encontrado na pasta atual | Versão registrada | **Arquivo-fonte ausente** | Recuperar o SQL original do histórico Git/backup; não reconstruir por suposição |
| `20260824171611 harden_kalatrace_rls_data_api_access` | Arquivo com essa versão não encontrado na pasta atual | Versão registrada | **Arquivo-fonte ausente** | Recuperar SQL original e revisar RLS/grants |
| `20260824234247 harden_public_security_definer_and_index_iec_nodes` | Arquivo com essa versão não encontrado na pasta atual | Versão registrada | **Arquivo-fonte ausente** | Recuperar SQL original |
| Formulários de pesquisa | `20260827120000_add_research_form_records.sql` | `20260827172835 add_research_form_records_and_links` | **Versão divergente** | Comparar SQL completo e schema antes de escolher versão canônica |
| Projetos/agentes locais | `20260827130000_add_projects_and_local_agent_control.sql` | `20260827174829 add_projects_and_local_agent_control` | **Versão divergente** | Comparar SQL completo e schema antes de escolher versão canônica |
| Evidência/relacionamentos | `20261005_epistemic_evidence_relations.sql` e `20261007135705_epistemic_evidence_relations.sql` | Versão `20261007135705` registrada | **Possível arquivo legado duplicado** | Confirmar origem no histórico Git; arquivar fora da pasta executável somente em PR separada |
| Uso de infraestrutura | `20261008170000_add_infrastructure_usage_rpc.sql` | `20261008190604 add_infrastructure_usage_rpc` | **Versão e implementação divergentes** | Recuperar o SQL aplicado; atualizar fonte canônica após comparação |
| Saúde/runtime da infraestrutura | Arquivo com versão correspondente não encontrado | `20261008191018 extend_infrastructure_health_rpc` registrada; funções/tabelas relacionadas existem | **Arquivo-fonte ausente** | Recuperar SQL original do Git/backup e comparar definições remotas |
| Workspace/CMC/agent governance | Arquivos `20260827140000` a `20260827210000` presentes | Tabelas consultadas não encontradas com nomes esperados | **Provavelmente não aplicado ou objetos renomeados** | Revisar dependências, RLS e uso pelo código antes de qualquer aplicação |

## Sequência de reconciliação aprovada para esta auditoria

1. Recuperar os quatro arquivos-fonte ausentes a partir do histórico Git, commits antigos ou backup confiável.
2. Obter o conteúdo SQL exato das migrações registradas remotamente, quando disponível, e comparar com os arquivos atuais e com as definições de funções, triggers, policies, grants, constraints, índices e colunas no banco.
3. Marcar cada versão como **correspondente**, **renomeada**, **duplicada**, **não aplicada intencionalmente** ou **não resolvida**.
4. Em uma PR separada, restaurar arquivos históricos sem executar SQL e corrigir divergências de nomes apenas depois de validar a estratégia suportada pelo Supabase CLI.
5. Avaliar os módulos workspace/CMC em uma mudança isolada, incluindo revisão de autorização/RLS e testes; não aplicar todos os arquivos em lote.
6. Só depois da revisão, planejar migrações novas para diferenças de schema comprovadas. Não editar a tabela de histórico manualmente e não reaplicar DDL de forma especulativa.

## Verificações pendentes

- Recuperação das migrações iniciais e da migração de saúde/runtime.
- Comparação integral dos SQLs divergentes.
- Decisão explícita sobre a família workspace/CMC.
- Teste real de RLS com duas sessões autenticadas separadas.
- Proteção de senha comprometida ainda precisa ser habilitada nas configurações de Auth do projeto.
- A tela de login de `index.html` permanece fora do escopo desta reconciliação e não foi alterada.

## Critério para encerrar

A reconciliação só será considerada concluída quando cada versão remota tiver uma fonte local confiável (ou uma exceção documentada), as diferenças de schema tiverem uma decisão registrada e a sequência de migração puder ser validada sem reaplicar mudanças existentes nem introduzir permissões indevidas.
