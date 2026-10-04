# KALATRACE API ↔ Frontend audit

API routes discovered: 115
Frontend explicit ktApi targets: 25
Frontend domain binding paths: 25
Frontend dynamic OpenAPI catalog: ENABLED (/openapi.json)
Dynamic catalog exposes all published API routes to the frontend explorer.

## Explicit frontend targets
- /acquisition/health
- /agent/instances
- /agent/status
- /agent/tasks
- /agent/tasks/
- /agent/tasks?project_id=
- /auth/login
- /auth/me
- /cmc/commands/execute
- /cmc/health
- /cmc/missions
- /cmc/persistent/missions
- /cmc/persistent/missions?project_id=
- /cmc/stats
- /cognitive-cycle/active
- /cognitive-cycle/health
- /cognitive-cycle/stats
- /curation/conflicts
- /curation/duplicates
- /curation/gaps
- /health
- /neo4j/graph
- /neo4j/health
- /neo4j/stats
- /openapi.json
- /persistence/health
- /projects
- /projects/from-template
- /projects/templates
- /research/forms
- /research/forms?limit=100
- /robotics/
- /robotics/status
- /validation/history
- /validation/stats
- /workspace/me
- /workspace/profiles
- /workspace/projects/

## Coverage model
- Domain GET bindings: live data panels on operational screens.
- Contextual GET/POST/PATCH/PUT/DELETE routes: OpenAPI catalog + explicit actions.
- Mutations are never auto-fired by the catalog; they require explicit UI action and backend authorization.
- Runtime validation against Supabase/Neo4j remains an environment-level check.
