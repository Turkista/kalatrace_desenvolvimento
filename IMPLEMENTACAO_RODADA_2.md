# KALATRACE — Rodada 2: Workspace / CMC / Local Agent

## Implementado nesta rodada

### Workspace e governança
- `workspace_profiles` sincroniza identidade básica com Supabase Auth via trigger.
- `project_invitations` permite convite por e-mail e role, sem service-role key no backend.
- Convites pendentes são aplicados automaticamente quando o usuário correspondente se cadastra.
- RLS foi ampliado para permitir acesso por `project_memberships` e administração por owner/administrator.
- Endpoints de membros e convites foram adicionados.

### Projects
- Templates persistidos em `project_templates`.
- Templates iniciais: vazio, científico, robótica, simulação e Knowledge Graph.
- `POST /projects/from-template` cria projetos com configuração inicial de módulos, engines, skills, CMC e Knowledge Graph.
- A tela de Projetos agora apresenta templates.

### CMC transversal
- Persistência durável para comandos, decisões, alocações de recursos e eventos.
- A criação de missão pelo endpoint runtime também grava a missão persistente usando o mesmo UUID.
- Comandos, decisões e alocações criados pelo CMC são persistidos.
- Endpoint para consultar artefatos de uma missão.
- O CMC continua sendo transversal e vinculado opcionalmente a qualquer projeto.

### Agente Local
- Criado `local_agent/runner.py` como conector operacional.
- O conector autentica como usuário normal, envia heartbeat, reivindica tarefas aprovadas e reporta resultado.
- Novos endpoints `/agent/runtime/heartbeat`, `/agent/runtime/claim` e `/agent/runtime/tasks/{task_id}/complete`.
- Criada persistência de `local_agent_instances`.
- `.env.example` documenta as variáveis opcionais do conector.
- O conector deliberadamente não executa código arbitrário: um handler/sandbox explícito é necessário para a etapa de coding.

### Frontend
- Workspace ganhou gestão visual de membros e convite.
- Projects ganhou catálogo de templates.
- Agente Local ganhou visualização de instâncias e ciclo operacional Task → Planning → Approval → Execution → Tests → Validation/Evolution.

### Correção estrutural encontrada
- A versão anterior continha registros de rotas CMC antes da criação do objeto `app`, o que tornava `import api.main` inválido. O bloco foi removido.

## Validação
- `python -m compileall -q kalatrace_oficial`: OK.
- Sintaxe dos blocos JavaScript de `index.html`: OK via `node --check`.
- Suíte existente: **487 passed**.

## Ainda não concluído

1. **Executor cognitivo/autônomo completo do Agente Local**: o runner já conversa com a fila, mas não possui um sandbox de coding/test execution integrado. Isso requer definir o ambiente de execução local e suas políticas.
2. **Administração de usuários no nível de Supabase Auth**: criação/reset administrativo de contas não foi implementado, deliberadamente, porque o backend usa publishable key e não service-role. O modelo de convite + auto-associação foi implementado como alternativa segura.
3. **CMC lifecycle completo**: ainda falta sincronizar automaticamente todas as transições internas do runtime para a persistência, inclusive timeline/eventos em cada mudança de estado.
4. **Auditoria completa endpoint-by-endpoint das engines**: ainda precisa ser feita com o sistema inteiro, especialmente frontend → API → engines → persistência.
5. **Neo4j end-to-end**: a auditoria estrutural continua pendente de um ambiente com as dependências/configuração do Neo4j disponível.

## Observação de credenciais
Nenhuma senha ou segredo real foi inserido. O projeto continua dependendo de `.env` local. O arquivo `.env.example` documenta Supabase, Neo4j e o conector do Agente Local.
