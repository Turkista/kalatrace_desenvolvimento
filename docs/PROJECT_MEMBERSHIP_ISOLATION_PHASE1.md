# KALATRACE — Isolamento por projeto: fase 1

## Decisão de arquitetura

O usuário pode compartilhar um projeto por meio de `project_memberships`. Não é necessário criar um Workspace multi-tenant nesta etapa. A identidade é verificada pelo Supabase Auth; o acesso ao projeto depende do proprietário ou de uma membership visível sob o token da sessão.

## Implementado nesta fase

- `require_project_access` valida o projeto usando o access token da requisição, consultando `projects` e `project_memberships`; não usa service-role.
- As rotas persistentes de missões CMC validam o acesso ao `project_id` antes de ler ou criar missões.
- A migration `20261015090000_enable_project_membership_cmc_access.sql` atualiza RLS para que membros possam ler missões do projeto; contribuição exige papel diferente de `viewer`; alteração/remoção exige `owner`, `administrator`, `developer` ou `operator`.
- A migration fornece um helper `SECURITY DEFINER` restrito a `authenticated`, limitado à identidade `auth.uid()`, para consultar o papel sem criar uma dependência recursiva entre políticas RLS.
- Testes unitários cobrem proprietário, membro, não membro e contexto de autenticação ausente; CI inclui o novo módulo de testes.

## Aplicação e verificação obrigatórias

1. Aplicar a migration no projeto Supabase correspondente antes de testar compartilhamento em ambiente real.
2. Testar com duas contas: proprietário e membro devem acessar o mesmo projeto conforme o papel; uma terceira conta sem membership deve receber 404.
3. Confirmar que `viewer` consegue ler, mas não criar/alterar/remover missões compartilhadas.
4. Verificar que `researcher` pode contribuir e que `operator` pode operar missões, sem conseguir administrar membros.
5. Confirmar que RLS está habilitado e que os helpers estão no schema `private`, com grants restritos.

## Fora do escopo — não considerar resolvido

Esta fase **não** completa o isolamento do Knowledge Graph. Os endpoints globais `/graph`, `/neo4j/graph`, `/neo4j/stats` e os componentes cognitivos ainda precisam de um contrato explícito de `project_id` e de uma estratégia de migração para nós/arestas legados. Não basta autenticar uma chamada para garantir autorização por projeto. Não foi possível confirmar a conectividade de produção nesta alteração; a validação real depende da migration aplicada e de testes com contas separadas.

## Próxima sequência

1. Inventariar quais tabelas e endpoints carregam `project_id`, `owner_id` ou apenas estado em memória.
2. Tornar o `project_id` obrigatório nos endpoints de leitura/escrita do Knowledge Graph que suportarem dados de projeto.
3. Marcar nós e relações no Neo4j com o escopo do projeto e excluir dados legados sem escopo das consultas compartilhadas.
4. Substituir os singletons mutáveis do grafo/orquestrador por contexto isolado por requisição/projeto ou armazenamento persistente devidamente escopado.
5. Adicionar testes de integração com duas contas e dois projetos antes de qualquer merge da fase seguinte.
