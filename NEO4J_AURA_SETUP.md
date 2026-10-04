# KALATRACE + Neo4j Aura

Esta versão adiciona a conexão do backend local ao Neo4j Aura para a camada persistente de Knowledge Graph.

## 1. Configure o ambiente local

Copie `.env.example` para `.env` e mantenha as configurações do Supabase. Depois preencha apenas no seu computador:

```env
NEO4J_URI=neo4j+s://c74047b0.databases.neo4j.io
NEO4J_USERNAME=c74047b0
NEO4J_PASSWORD=SUA_SENHA_DO_NEO4J
NEO4J_DATABASE=c74047b0
NEO4J_ENABLED=true
```

A senha não está incluída neste pacote.

## 2. Instale as dependências

```powershell
pip install -r requirements.txt
```

## 3. Teste a conexão

```powershell
python scripts/test_neo4j_connection.py
```

## 4. Arquitetura

- Supabase/PostgreSQL: Auth, RLS, IEC, Evidence, Predictions e Simulations.
- Neo4j Aura: KnowledgeNode e KnowledgeEdge.
- IEC não é convertido em KnowledgeNode. A relação IEC → KnowledgeNode será tratada explicitamente em camada posterior.

A conexão usa o driver oficial Neo4j e `neo4j+s`, com TLS.
