# KALATRACE — Auditoria de endpoints e fluxos de informação

**Data:** 15/10/2026  
**Repositório:** `Turkista/kalatrace_desenvolvimento`  
**Base analisada:** `main`, commit `4fdabb59c05a160e3fc8b9f3c24945e17c78d549)  
**Branch de trabalho:** `audit/epistemic-isolation-neo4j-hardening`

## Escopo

A revisão percorre a interface publicada em GitHub Pages, a API FastAPI, middleware de autenticação, contexto de persistência por requisição, módulos cognitivos, armazenamento de evidências, formulários de pesquisa, Supabase/PostgreSQL e Neo4j Aura. A contagem estática encontrou 122 declarações de rotas diretamente em `api/main.py`; há ainda rotas registradas pelo router de formulários e rotas automáticas do FastAPI. A contagem de decoradores não deve ser confundida com uma lista completa de operações registradas no OpenAPI.

## Fluxo de referência

1. **Interface** (`index.html`, `login.html`): login por `POST /auth/login`; validação por `GET /auth/me`; token mantido em `sessionStorage`; chamadas autenticadas à API.
2. **Autorização** (`integrations/auth.py`): verifica token Supabase, aplica a allowlist opcional `KALATRACE_ALLOWED_USER_IDS` e estabelece o contexto de persistência com token e ID do usuário.
3. **Operação cognitiva** (`/cognitive-cycle/run`): o orquestrador executa o ciclo, a IEC é persistida no Supabase com o proprietário da sessão e a projeção é sincronizada com Neo4j.
4. **Evidências**: o middleware cria um `EvidenceStore` por requisição; evidências e relações são hidratadas pelo token atual e persistidas com as políticas RLS do Supabase.
5. **Formulários de pesquisa**: `/research/forms` usa o router `api/research_forms.py`; os registros ficam em `research_form_records` e o histórico em `research_form_record_events`.
6. **Grafo persistente**: Neo4j armazena a projeção estrutural (`KnowledgeNode`, `KnowledgeEdge`) e entidades IEC; o Supabase continua sendo a fonte transacional relacional e a fronteira de autorização por usuário.

## Correções feitas nesta branch

- `/neo4j/health` e `/neo4j/stats` deixam de ser exceções públicas ao middleware. Exigem token válido como as demais rotas operacionais.
- A resposta de conectividade do Neo4j não inclui URI nem nome de usuário.
- Respostas de erro dos endpoints de saúde/estatísticas/grafo não propagam a exceção bruta do driver, reduzindo vazamento de detalhes internos.
- `_hydrate_iec_from_supabase` não consulta nem preenche o grafo global em memória. Cada leitura de IEC passa pelo Supabase usando o token da requisição, permitindo que RLS decida se a IEC é visível à sessão.
- Foram adicionados testes de regressão para autenticação das rotas operacionais, isolamento da consulta de IEC e sanitização da resposta de conectividade.

## Riscos residuais que exigem uma rodada própria

### Alto — estado cognitivo e grafo em memória compartilhados pelo processo

`api/main.py` instancia `graph = KnowledgeGraph()` e um único `CognitiveOrchestrator` global. O ciclo cognitivo e algumas rotas de curadoria/consulta usam esses objetos compartilhados. Embora o Supabase aplique RLS, o estado transitório global não tem, por si só, uma chave de proprietário. A correção de cache IEC desta branch fecha o atalho identificado no endpoint epistemológico, mas **não prova isolamento multiusuário de todos os endpoints que usam o grafo ou o orquestrador globais**.

A próxima correção estrutural deve associar estado cognitivo e grafo ao usuário/projeto, ou reconstruí-los a partir de dados autorizados por requisição. Antes de trocar a estratégia global, é necessário mapear os contratos e os testes de ciclo cognitivo, aquisição, curadoria e robótica para não quebrar o estado esperado pelo produto.

### Alto — isolamento do grafo Neo4j

A camada de integração atual consulta o grafo Neo4j de forma global em `/neo4j/graph` e calcula estatísticas agregadas. As rotas operacionais agora exigem autenticação, mas autenticação não equivale a autorização por proprietário. Deve-se confirmar se a implantação está deliberadamente limitada a uma única identidade por `KALATRACE_ALLOWED_USER_IDS`. Se houver mais de um usuário, os nós, arestas e consultas precisam incluir uma fronteira de usuário/projeto consistente com a política do Supabase.

### Médio — allowlist opcional

`user_is_allowed` permite qualquer usuário autenticado quando `KALATRACE_ALLOWED_USER_IDS` está vazio. Isso pode ser intencional em desenvolvimento, mas a implantação de produção deve confirmar que a variável está definida se o sistema for de acesso restrito. Não alterei o comportamento padrão para evitar bloquear o login existente sem confirmação da configuração de produção.

### Médio — operações multi-etapa entre bancos

A gravação no Supabase e a sincronização no Neo4j são operações separadas. Uma falha depois da primeira gravação pode deixar o registro relacional persistido e a projeção do grafo atrasada. A tabela de status/outbox já existe no esquema; é necessário validar em execução a recuperação de pendências e idempotência do reconciliador, inclusive depois de reinício do backend.

### Médio — cobertura do frontend

A interface possui chamadas explícitas e também um explorador dinâmico baseado no OpenAPI. As chamadas com parâmetros dinâmicos (por exemplo, IDs de tarefa/projeto) não podem ser validadas com comparação literal de strings; a verificação deve comparar método HTTP e template de rota. O CI já verifica sintaxe dos scripts inline e roda testes focados de autenticação, IEC e persistência, mas isso não substitui um teste ponta a ponta com Supabase e Neo4j reais.

## Validação

A suíte de CI definida em `.github/workflows/tests.yml` executa testes focados e valida sintaxe JavaScript de `index.html` e `login.html`. Os testes novos devem ser confirmados na execução do workflow do pull request. Nenhuma alteração nesta branch foi aplicada diretamente à `main`; a configuração remota de produção não é acessível por leitura do código e deve ser validada no painel do serviço.

## Critérios para concluir a auditoria

- [ ] CI verde no pull request.
- [ ] Confirmar configuração de `KALATRACE_ALLOWED_USER_IDS` no backend publicado.
- [ ] Testar login, logout e retomada de projeto no frontend publicado.
- [ ] Testar consulta, gravação e recuperação de IEC/evidência com duas identidades de teste.
- [ ] Verificar que um usuário não consegue consultar IEC, evidência, nó, aresta ou estado cognitivo de outro.
- [ ] Testar falha/retomada entre gravação Supabase e sincronização Neo4j.
- [ ] Validar o estado real do Neo4j Aura e a correspondência entre projeção e fonte relacional.
