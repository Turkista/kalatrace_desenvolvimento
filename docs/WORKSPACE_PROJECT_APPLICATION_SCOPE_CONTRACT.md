# KALATRACE — Contrato de escopo Workspace → Project → Application

**Status:** proposta técnica para orientar a próxima implementação; ainda não é contrato implementado.  
**Repositório:** `Turkista/kalatrace_desenvolvimento`  
**Branch:** `audit/epistemic-isolation-neo4j-hardening`  
**Princípio:** não alterar a `main` nem ativar isolamento parcial que possa misturar estado cognitivo de usuários/projetos.

## 1. Decisões de arquitetura que devem permanecer invariáveis

- **KALATRACE Control** é a infraestrutura de controle; não é um projeto de domínio.
- **Workspace** representa o contexto de identidade, membros, papéis e permissões. A implementação atual de `/workspace/me` monta um objeto de resposta a partir do usuário autenticado; isso não prova a existência de um Workspace persistido nem de `workspace_id`.
- **Project** é uma unidade persistente de trabalho. Já existem endpoints/tabelas para projetos e vários contratos usam `project_id`.
- **Application** é uma aplicação registrada que pode ser disponibilizada dentro de um Project; MEDIKALAT, SkinMap, YANSIX, Turkista, Robótica e Agente Local não devem ser codificados como regras dispersas de autorização.
- **IEC ≠ KnowledgeNode**. A IEC é a unidade epistemológica/transacional; KnowledgeNode é a entidade estrutural projetada no Knowledge Graph. A relação explícita continua sendo `(:IEC)-[:REPRESENTS]->(:KnowledgeNode)`.
- **Supabase/PostgreSQL** é a fonte de verdade transacional e a fronteira de autorização via token/RLS. **Neo4j** é a projeção estrutural do grafo; a autenticação na API não autoriza, por si só, acesso a todo o grafo.
- **Agente Local** permanece aprovação-gated, sandboxed, auditado e com rollback; não marcar um executor como conectado sem uma instância real.

## 2. Contrato de contexto por requisição

Toda operação de domínio deve resolver o contexto nesta ordem:

1. Validar o token Supabase e obter `user_id` do token verificado; nunca confiar num `user_id` enviado pelo cliente.
2. Resolver o Workspace persistido e verificar associação/membership do usuário.
3. Resolver um `project_id` UUID explícito e confirmar membership/permissão sobre esse Project no Workspace. Não inferir o Project pelo nome, slug, ordem de exibição ou variável global.
4. Resolver `application_id`/binding, quando a operação pertence a uma aplicação. Confirmar que a aplicação está habilitada para aquele Project.
5. Criar um contexto imutável da requisição contendo `user_id`, `workspace_id`, `project_id`, permissões e token. Serviços de domínio recebem esse contexto explicitamente.
6. Aplicar o mesmo escopo à leitura relacional, ao estado cognitivo, às consultas Neo4j e aos eventos de auditoria.

Se o contrato de escopo não puder ser resolvido, operações de escrita/leitura de domínio devem falhar de forma explícita (401/403/404 conforme o caso), em vez de cair para um grafo global.

## 3. Estado cognitivo e Knowledge Graph

### Estado em memória

A API atualmente instancia objetos globais em `api/main.py`, incluindo `graph = KnowledgeGraph()` e `cognitive_orchestrator = CognitiveOrchestrator(...)`. Há handlers de grafo, curadoria, validação, aquisição, ciclo cognitivo, robótica e CMC que consultam ou mutam objetos globais. O middleware autentica as chamadas, mas muitos desses handlers não recebem `Request` e não podem aplicar autorização por usuário/projeto internamente.

**Não basta** substituir o objeto global por uma instância vazia a cada requisição: isso quebra o histórico do ciclo e as ligações entre engines. Também não basta usar apenas `user_id` como chave, porque o mesmo usuário pode ter vários projetos e aplicações.

Contrato-alvo:
- chave lógica mínima do estado mutável: `(workspace_id, project_id, application_id)`; módulos realmente compartilhados podem ter escopo de Workspace ou plataforma, declarado explicitamente.
- nenhuma IEC, evidência, aresta, hipótese, ciclo, histórico de validação ou estatística de domínio deve ser compartilhada implicitamente entre chaves.
- o estado durável deve ser reconstruível a partir de dados autorizados; memória do processo é cache/otimização, não fonte de autorização.
- instâncias e caches devem ter política de ciclo de vida, concorrência, invalidação e recuperação após restart.
- operações puramente consultivas/estáticas, como definição do workflow, podem continuar sem estado de domínio; estatísticas devem declarar seu escopo.

### Neo4j

Antes de alterar consultas, definir o modelo de propriedades e índices:
- IEC: identidade persistente e escopo de Workspace/Project conforme o contrato de dados relacional.
- KnowledgeNode: ID estrutural próprio, tipo e escopo de Project; não reutilizar o ID da IEC como se fossem a mesma entidade.
- KnowledgeEdge: relação com endpoints pertencentes ao mesmo escopo autorizado, com validação no serviço.
- `REPRESENTS`: associação explícita entre IEC e KnowledgeNode, também scoped.
- cada query de leitura, estatística, atualização e sincronização deve filtrar pelo escopo verificado; endpoints de grafo não podem retornar agregados globais para usuários comuns.
- planejar backfill/migração dos nós existentes antes de ativar filtros obrigatórios; registros antigos sem escopo não devem ser atribuídos por suposição.

## 4. Matriz inicial de handlers que dependem de estado compartilhado

Inventário estático de `api/main.py` na branch de auditoria. É uma triagem por referências a objetos globais, não uma prova de vulnerabilidade em cada rota.

| Área | Rotas/handlers observados | Dependência | Ação necessária |
|---|---|---|---|
| Grafo | `GET /graph` | Serializa `graph.nodes`, `knowledge_nodes` e `edges` globais | Responder somente para o escopo autorizado |
| Curadoria | `GET /curation/gaps`, `/curation/duplicates`, `/curation/conflicts` | Recebem o grafo global | Injetar grafo scoped |
| Ciclo cognitivo | `POST /cognitive-cycle/run`, `GET /cognitive-cycle/active`, `/stats`, `/strategic-plan`, `/{iec_id}` | Orquestrador/coordenador globais | Isolar estado e histórico por chave de contexto |
| Aquisição | `/acquisition/search`, `/search-and-build`, `/build-iecs`, endpoints de stats/health | Pipeline/builder e/ou grafo global | Separar execução e persistência por escopo |
| Validação | `/validation/*` | Validator construído com grafo e store compartilhados | Injetar estado scoped e validar ownership da IEC |
| IEC | `POST /iec` e ingestão | Engine e pipeline de ingestão globais | Persistir com escopo autorizado antes da projeção |
| Robótica/CMC | `/robotics/*`, `/cmc/*` | Instâncias globais com estado de missão/robô | Declarar escopo de plataforma vs Project; aplicar autorização a missões e recursos |
| Neo4j | `/neo4j/graph`, `/neo4j/stats`, sincronização | Consulta/projeção sem filtro completo por dono/projeto | Adicionar scoping e migração de dados antes de liberar multiusuário |

Nota: a assinatura sem `Request` não significa que a rota esteja pública — o middleware protege o endpoint —, mas significa que o handler não consegue obter diretamente o contexto verificado. O problema é o estado compartilhado, não a mera presença/ausência do parâmetro.

## 5. Sequência de implementação segura

1. **Contrato e inventário:** validar este documento com o esquema real de Workspace/memberships/Projects/Applications e as políticas RLS existentes. Não presumir tabelas ou colunas que ainda não existem.
2. **Persistência e autorização:** identificar migrations e métodos do cliente Supabase para Project membership; fechar leitura/escrita cross-project com testes RLS. Criar Workspace persistido somente depois de decidir como migrar os usuários/projetos atuais.
3. **Contexto explícito:** introduzir um resolvedor de contexto por requisição; exigir Project UUID para rotas de domínio que precisam de escopo. Manter rotas estáticas de metadata/workflow separadas.
4. **Estado em memória:** alterar primeiro uma fatia vertical (IEC + evidências + consulta de grafo), com fábrica/registro scoped e reconstrução de dados autorizados; não mudar todos os engines num único patch.
5. **Neo4j:** migrar nós/arestas com escopo; atualizar upserts, consultas, stats e reconciliação; testar idempotência e impedir consultas sem escopo.
6. **Ciclo cognitivo e módulos dependentes:** mover coordenador, pipeline, validadores, acquisition, curation e módulos derivados para o contexto scoped, preservando contratos públicos e a separação IEC/KnowledgeNode.
7. **CMC/Robótica/Agente Local:** definir o que é infraestrutura compartilhada e o que pertence ao Project; manter comandos de execução sob aprovação e trilha de auditoria.
8. **Frontend:** somente depois do contrato backend, trocar a seleção hardcoded por um Project UUID ativo e binding de Application validado pelo servidor.
9. **Validação final:** dois usuários × dois projetos, testes de leitura/escrita cruzada, ciclo cognitivo persistido, falha entre Supabase/Neo4j, reinício da API, logout/troca de projeto, e conferência das rotas do OpenAPI.

## 6. Critérios de aceite

- [ ] Workspace persistido e memberships documentados; sem fingir que `/workspace/me` já os implementa.
- [ ] Project UUID validado pelo servidor em cada operação de domínio.
- [ ] Application Registry/Binding/Configuration definido antes de remover hardcodes de frontend.
- [ ] Nenhum estado mutável de domínio é global sem escopo declarado.
- [ ] Nenhuma query Neo4j operacional retorna dados de outro Project/Workspace.
- [ ] IEC e KnowledgeNode continuam entidades distintas com associação explícita.
- [ ] RLS e autorização de API são testadas com pelo menos duas identidades e dois Projects.
- [ ] Reconciliação Supabase → Neo4j é idempotente e recupera falhas/reinícios.
- [ ] CI verde e teste de integração executado contra serviços reais antes de merge.

## 7. Limites desta etapa

Este documento não cria tabelas, não altera o comportamento do frontend e não transforma um serviço externo em “conectado”. A configuração de produção e os serviços remotos ainda precisam ser verificados com acesso ao ambiente. A implementação deve começar pela validação dos contratos de dados/RLS, e não por um proxy que entregue um grafo vazio ou por uma alteração ampla e não testada dos engines.
