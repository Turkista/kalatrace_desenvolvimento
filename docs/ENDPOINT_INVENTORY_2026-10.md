# KALATRACE — Inventário de endpoints (estático)

Base: `api/main.py` e router `api/research_forms.py` na branch `audit/epistemic-isolation-neo4j-hardening`.
Este documento é um inventário estático de decoradores. Rotas automáticas do FastAPI (`/openapi.json`, `/docs`, `/redoc`) não aparecem nos decoradores e podem depender da configuração do app. O middleware de autenticação verifica o caminho completo contra `PUBLIC_PATHS`; as demais rotas exigem token válido quando `KALATRACE_AUTH_REQUIRED=true`.

**Contagem estática:** 123 rotas declaradas nos dois arquivos (método + caminho + handler). Rotas dinâmicas são templates, por exemplo `/agent/tasks/{task_id}`.

**Rotas públicas após a alteração desta branch:** `/health`, `/docs`, `/redoc`, `/openapi.json`, `/auth/signup`, `/auth/login`. Os endpoints de saúde e estatísticas do Neo4j não estão na lista pública.


## /acquisition

| Método | Caminho | Handler |
|---|---|---|
| POST | `/acquisition/build-iecs` | `build_iecs_from_records` |
| GET | `/acquisition/build-stats` | `get_acquisition_build_stats` |
| GET | `/acquisition/health` | `get_acquisition_health` |
| POST | `/acquisition/search` | `search_acquisition` |
| POST | `/acquisition/search-and-build` | `search_and_build_acquisition` |
| GET | `/acquisition/stats` | `get_acquisition_stats` |

## /agent

| Método | Caminho | Handler |
|---|---|---|
| GET | `/agent/instances` | `local_agent_instances` |
| POST | `/agent/runtime/claim` | `agent_runtime_claim` |
| POST | `/agent/runtime/heartbeat` | `agent_runtime_heartbeat` |
| POST | `/agent/runtime/tasks/{task_id}/complete` | `agent_runtime_complete` |
| POST | `/agent/runtime/tasks/{task_id}/execute` | `agent_runtime_execute` |
| GET | `/agent/status` | `local_agent_status` |
| GET | `/agent/tasks` | `list_agent_tasks` |
| POST | `/agent/tasks` | `create_agent_task` |
| PATCH | `/agent/tasks/{task_id}` | `update_agent_task` |
| POST | `/agent/tasks/{task_id}/approve` | `approve_agent_task` |
| POST | `/agent/tasks/explicit-plan` | `create_explicit_agent_plan` |
| POST | `/agent/tasks/plan` | `plan_agent_task` |

## /auth

| Método | Caminho | Handler |
|---|---|---|
| POST | `/auth/login` | `auth_login` |
| POST | `/auth/logout` | `auth_logout` |
| GET | `/auth/me` | `auth_me` |
| POST | `/auth/signup` | `auth_signup` |

## /cmc

| Método | Caminho | Handler |
|---|---|---|
| POST | `/cmc/commands` | `issue_command` |
| POST | `/cmc/commands/execute` | `execute_command` |
| POST | `/cmc/decisions` | `record_decision` |
| GET | `/cmc/health` | `get_cmc_health` |
| POST | `/cmc/missions` | `create_mission` |
| GET | `/cmc/missions/{mission_id}` | `get_mission_overview` |
| POST | `/cmc/missions/{mission_id}/evolve` | `evolve_cmc_mission` |
| POST | `/cmc/missions/{mission_id}/transition` | `transition_mission` |
| POST | `/cmc/persistent/{artifact_type}` | `cmc_persist_artifact` |
| GET | `/cmc/persistent/missions` | `list_persistent_cmc_missions` |
| POST | `/cmc/persistent/missions` | `persist_cmc_mission` |
| GET | `/cmc/persistent/missions/{mission_id}/artifacts` | `cmc_mission_artifacts` |
| POST | `/cmc/resources` | `register_resource` |
| POST | `/cmc/resources/allocate` | `allocate_resource` |
| POST | `/cmc/resources/release` | `release_resource` |
| GET | `/cmc/robots` | `list_cmc_robots` |
| POST | `/cmc/robots/dispatch` | `dispatch_mission_to_robot` |
| GET | `/cmc/stats` | `get_cmc_stats` |

## /cognitive-cycle

| Método | Caminho | Handler |
|---|---|---|
| GET | `/cognitive-cycle/{iec_id}` | `get_cognitive_cycle_state` |
| GET | `/cognitive-cycle/active` | `list_active_cognitive_cycles` |
| GET | `/cognitive-cycle/health` | `get_cognitive_cycle_health` |
| POST | `/cognitive-cycle/run` | `run_cognitive_cycle` |
| GET | `/cognitive-cycle/stats` | `get_cognitive_cycle_stats` |
| GET | `/cognitive-cycle/strategic-plan` | `get_cognitive_cycle_strategic_plan` |
| GET | `/cognitive-cycle/workflow` | `get_cognitive_cycle_workflow` |

## /curation

| Método | Caminho | Handler |
|---|---|---|
| GET | `/curation/conflicts` | `get_conflicts` |
| GET | `/curation/duplicates` | `get_duplicates` |
| GET | `/curation/gaps` | `get_gaps` |

## /epistemic

| Método | Caminho | Handler |
|---|---|---|
| GET | `/epistemic/iec/{iec_id}` | `get_epistemic_conclusion` |

## /events

| Método | Caminho | Handler |
|---|---|---|
| POST | `/events/publish` | `publish_event` |
| GET | `/events/subscribers/{event_type}` | `get_event_subscribers` |
| GET | `/events/types` | `list_event_types` |

## /evidence

| Método | Caminho | Handler |
|---|---|---|
| GET | `/evidence` | `list_evidence` |
| POST | `/evidence` | `create_evidence` |
| DELETE | `/evidence/{evidence_id}` | `delete_evidence` |
| GET | `/evidence/{evidence_id}` | `get_evidence` |
| PATCH | `/evidence/{evidence_id}/confidence` | `update_evidence_confidence` |
| GET | `/evidence/for-iec/{iec_id}` | `get_evidence_for_iec` |
| POST | `/evidence/link` | `link_evidence_to_iec` |
| GET | `/evidence/strength/{iec_id}` | `get_evidence_strength` |

## /evidence-validation

| Método | Caminho | Handler |
|---|---|---|
| POST | `/evidence-validation/compare` | `compare_iec_support` |
| POST | `/evidence-validation/diagnostic` | `generate_iec_diagnostic` |
| POST | `/evidence-validation/evidence/{evidence_id}` | `validate_evidence` |
| POST | `/evidence-validation/gaps` | `analyze_iec_evidence_gaps` |
| GET | `/evidence-validation/history` | `get_evidence_validation_history` |
| POST | `/evidence-validation/iec` | `validate_iec_epistemic` |
| POST | `/evidence-validation/rank` | `rank_iec_support` |
| GET | `/evidence-validation/stats` | `get_evidence_validation_stats` |

## /graph

| Método | Caminho | Handler |
|---|---|---|
| GET | `/graph` | `get_graph` |

## /health

| Método | Caminho | Handler |
|---|---|---|
| GET | `/health` | `get_health` |

## /iec

| Método | Caminho | Handler |
|---|---|---|
| POST | `/iec` | `create_iec` |

## /infrastructure

| Método | Caminho | Handler |
|---|---|---|
| GET | `/infrastructure/usage` | `infrastructure_usage` |
| GET | `/infrastructure/watchdog/events` | `infrastructure_watchdog_events` |
| GET | `/infrastructure/watchdog/history` | `infrastructure_watchdog_history` |
| POST | `/infrastructure/watchdog/run` | `infrastructure_watchdog_run` |
| GET | `/infrastructure/watchdog/runtime` | `infrastructure_watchdog_runtime` |
| GET | `/infrastructure/watchdog/trends` | `infrastructure_watchdog_trends` |

## /neo4j

| Método | Caminho | Handler |
|---|---|---|
| GET | `/neo4j/graph` | `get_neo4j_graph` |
| GET | `/neo4j/health` | `get_neo4j_health` |
| GET | `/neo4j/stats` | `get_neo4j_stats` |

## /persistence

| Método | Caminho | Handler |
|---|---|---|
| GET | `/persistence/health` | `get_persistence_health` |
| GET | `/persistence/sync` | `list_knowledge_sync` |
| POST | `/persistence/sync/iec/{iec_id}` | `sync_iec_to_neo4j` |

## /projects

| Método | Caminho | Handler |
|---|---|---|
| GET | `/projects` | `list_projects` |
| POST | `/projects` | `create_project` |
| DELETE | `/projects/{project_id}` | `delete_project` |
| PATCH | `/projects/{project_id}` | `update_project` |
| GET | `/projects/{project_id}/members` | `project_members` |
| POST | `/projects/from-template` | `project_from_template` |
| GET | `/projects/templates` | `project_templates` |

## /research

| Método | Caminho | Handler |
|---|---|---|
| GET | `/research/forms` | `list_research_forms` |
| POST | `/research/forms` | `create_research_form` |

## /robotics

| Método | Caminho | Handler |
|---|---|---|
| GET | `/robotics/{robot_id}` | `get_robot` |
| POST | `/robotics/connect` | `connect_robot` |
| POST | `/robotics/disconnect` | `disconnect_robot` |
| POST | `/robotics/error` | `report_robot_error` |
| POST | `/robotics/mission/complete` | `complete_robot_mission` |
| POST | `/robotics/mission/start` | `start_robot_mission` |
| POST | `/robotics/object-detected` | `report_robot_object_detected` |
| POST | `/robotics/sensor` | `update_robot_sensor` |
| GET | `/robotics/status` | `get_robotics_status` |

## /security

| Método | Caminho | Handler |
|---|---|---|
| GET | `/security/modules/{module_name}/permissions` | `list_module_permissions` |
| POST | `/security/modules/{module_name}/permissions` | `grant_module_permission` |
| DELETE | `/security/modules/{module_name}/trust` | `untrust_module` |
| POST | `/security/modules/{module_name}/trust` | `trust_module` |
| GET | `/security/modules/{module_name}/trusted` | `is_module_trusted` |

## /validation

| Método | Caminho | Handler |
|---|---|---|
| POST | `/validation/all` | `validate_all_structural` |
| GET | `/validation/conflicts` | `get_structural_conflicts` |
| GET | `/validation/history` | `get_structural_validation_history` |
| POST | `/validation/iec/{iec_id}` | `validate_iec_structural` |
| GET | `/validation/report` | `get_structural_report` |
| GET | `/validation/stats` | `get_structural_validation_stats` |
| GET | `/validation/weak` | `get_weak_knowledge` |

## /workspace

| Método | Caminho | Handler |
|---|---|---|
| GET | `/workspace/me` | `workspace_me` |
| GET | `/workspace/profiles` | `workspace_profiles` |
| GET | `/workspace/projects/{project_id}/invitations` | `workspace_project_invitations` |
| POST | `/workspace/projects/{project_id}/invitations` | `workspace_create_invitation` |
| POST | `/workspace/projects/{project_id}/invitations/{invitation_id}/revoke` | `workspace_revoke_invitation` |
| GET | `/workspace/projects/{project_id}/members` | `workspace_project_members` |
| DELETE | `/workspace/projects/{project_id}/members/{user_id}` | `workspace_remove_member` |
| PATCH | `/workspace/projects/{project_id}/members/{user_id}` | `workspace_update_member_role` |

## Limites desta revisão

- A presença de uma rota não comprova que o serviço externo esteja disponível em produção.
- A proteção de autenticação não substitui autorização por proprietário/projeto nos dados do grafo.
- Chamadas do frontend que montam o caminho com IDs ou query strings precisam ser comparadas ao template e ao método HTTP, não por igualdade literal.
