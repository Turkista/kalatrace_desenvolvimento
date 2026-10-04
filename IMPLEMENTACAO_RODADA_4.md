# KALATRACE — Rodada 4

## Implementado nesta rodada

### Agente Local — coding controlado
- Adicionada camada `local_agent/code_workspace.py` para alterações explícitas de arquivos.
- Operações permitidas: `create_file` e `replace_text`.
- Limites de tamanho, quantidade de operações e payload total.
- Path traversal bloqueado.
- `replace_text` exige exatamente uma ocorrência para evitar alterações ambíguas.
- Backup automático dos arquivos alterados.
- Registro de auditoria em `.kalatrace_agent/audit/`.
- Rollback das alterações a partir do resultado auditado.
- Suporte a `code_dry_run` e `code_apply` no sandbox.

### Coding + validação
- `LocalAgentRunner` passou a anunciar `controlled_code_changes`.
- Uma tarefa de código pode declarar `post_checks` (ex.: pytest/compileall/node_check).
- Se um pós-teste falhar, `auto_rollback` pode restaurar os arquivos alterados.
- O fluxo continua sem shell arbitrário e sem `shell=True`.

### Governança de execução
- Aprovação agora grava `approved_by` e `approved_at` e adiciona evento ao `execution_log`.
- Endpoint de execução não aceita mais uma especificação diferente da especificação aprovada persistida.
- Tarefas sem `execution_spec` não são executadas pelo endpoint de sandbox.

### CMC
- Persistência de timeline ganhou RPC atômico `append_cmc_mission_timeline`.
- Endpoint de transição recupera missão persistida quando ela não existe no runtime atual.
- Transições continuam validadas pela `MissionStateMachine`.
- A timeline persistida é atualizada junto do evento da transição.

### Correção estrutural
- Removidos blocos duplicados de endpoints CMC/sandbox no `api/main.py`.
- A duplicação fazia `import api.main` falhar antes da inicialização do `app`.

### Frontend
- Painel do Agente Local agora permite declarar `code_apply`/`code_dry_run` e uma especificação JSON explícita de alterações e pós-testes.

## Validação
- `python -m pytest -q`: **495 passed**.
- `py_compile`: OK para API, Local Agent e integração Supabase.

## Limitações restantes
1. O coding agent ainda não possui um LLM/planner autônomo embutido; ele executa especificações de alterações produzidas por uma camada de planejamento.
2. O executor local real precisa ser conectado ao ambiente da máquina do usuário com `.env` configurado.
3. A validação E2E contra Supabase/Neo4j requer credenciais e migrations aplicadas no ambiente real.
4. A auditoria completa endpoint-by-endpoint e engine-by-engine ainda precisa de execução real com os serviços disponíveis.
5. Administração de usuários do Supabase Auth continua deliberadamente sem `service_role` no frontend/cliente.

## Credenciais
Nenhuma credencial real foi adicionada ao pacote.
