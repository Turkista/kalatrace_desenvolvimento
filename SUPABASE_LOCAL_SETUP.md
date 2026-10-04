# KALATRACE local + Supabase online

This build keeps the KALATRACE cognitive engines on the local computer while using Supabase online for Auth and PostgreSQL persistence.

## 1. Configure local environment

Copy `.env.example` to `.env` and fill in:

- `SUPABASE_URL=https://kedyzontvnailtwpacvz.supabase.co`
- `SUPABASE_PUBLISHABLE_KEY=<your publishable key>`
- `KALATRACE_AUTH_REQUIRED=true`

Never put a Supabase secret/service-role key in `.env` if the file may be shared with the frontend or committed to Git.

## 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 3. Start the local API

```powershell
uvicorn api.main:app --reload
```

The API remains local, normally at `http://127.0.0.1:8000`.

## 4. Authentication flow

Public endpoints:

- `POST /auth/signup`
- `POST /auth/login`
- `GET /health`
- Swagger/OpenAPI documentation

Protected endpoints require:

```text
Authorization: Bearer <supabase_access_token>
```

`GET /auth/me` returns the verified Supabase user.

## 5. Persistence boundary

The local `POST /iec` endpoint creates and processes the IEC locally, then persists the IEC in Supabase using the authenticated user's token.

The local `POST /evidence` endpoint does the same for evidence.

The access token is forwarded to PostgREST, so the PostgreSQL RLS policies enforce ownership. The local backend does not use a service-role key.

## 6. Important architectural boundary

Do not collapse `KnowledgeNode` and `IEC`.

- `knowledge_nodes` / `knowledge_edges` are reserved for the structural Knowledge Graph.
- `iecs` is the epistemological/comparative IEC layer.
- `iec_nodes` explicitly models IEC -> KnowledgeNode derivation/association.

The current backend still has legacy in-memory graph behavior where IEC objects are the graph nodes. This integration deliberately persists IECs without pretending that those IEC objects are already the new persistent KnowledgeNodes. The next architectural migration can move the graph persistence to Neo4j while keeping the Supabase IEC/Evidence boundary intact.

## 7. Neo4j

When the Neo4j account is ready, configure the Neo4j URI, username and password separately. Neo4j will become the specialized graph persistence layer; Supabase remains the operational/authentication database.
