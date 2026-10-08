"""
api/main.py — API do KALATRACE.

Roda com:
    uvicorn api.main:app --reload

Arquitetura:

    Supabase PostgreSQL/Auth
        ├── autenticação
        ├── identidade
        └── persistência relacional

    Neo4j Aura
        ├── Knowledge Graph persistente
        ├── KnowledgeNode
        └── KnowledgeEdge

    KALATRACE Engine
        ├── execução local
        ├── inferência
        ├── governança
        ├── evolução
        └── metacognição

IMPORTANTE:

    IEC e KnowledgeNode são conceitos distintos.

    IEC
        = unidade epistemológica/comparativa.

    KnowledgeNode
        = unidade estrutural persistente do Knowledge Graph.

    Uma IEC pode originar ou referenciar um KnowledgeNode,
    mas IEC não deve ser tratada como sinônimo de KnowledgeNode.

O .env é carregado ANTES das integrações que dependem de
variáveis de ambiente, especialmente Neo4j Aura e Supabase.
"""

from __future__ import annotations


# ==========================================================
# ENVIRONMENT
# ==========================================================

import os
from contextvars import ContextVar
import subprocess

from dotenv import load_dotenv

# IMPORTANTE:
# Carrega o .env antes dos imports das integrações.
load_dotenv(override=True)


# ==========================================================
# STANDARD LIBRARY
# ==========================================================

from typing import Any, Dict, List, Optional
from types import SimpleNamespace


# ==========================================================
# FASTAPI
# ==========================================================

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ==========================================================
# KALATRACE CORE
# ==========================================================

from engines.base.base_engine import CoreEngine
from graph.knowledge_graph import KnowledgeGraph
from inference.inference import infer
from governance.evaluator import Evaluator
from evolution.optimizer import Optimizer
from metacognition.self_model import SelfModel
from metacognition.observer import Observer
from metacognition.metrics import compute_system_health
from curation.curation import (
    detect_duplicates,
    detect_gaps,
    detect_conflicts,
)
from utils.embeddings import is_using_fallback


# ==========================================================
# COGNITIVE ORCHESTRATOR
# ==========================================================

from engines.cognitive_orchestrator.cognitive_orchestrator_engine import (
    CognitiveOrchestrator,
)


# ==========================================================
# ACQUISITION
# ==========================================================

from acquisition.acquisition_pipeline import AcquisitionPipeline
from acquisition.iec_builder import IECBuilder


# ==========================================================
# ROBOTICS
# ==========================================================

from skills.robotics.robotics_skill import RoboticsSkill
from skills.robotics.robotics_api import RoboticsAPI


# ==========================================================
# VALIDATION / EVIDENCE
# ==========================================================

from validation.validation_engine import ValidationEngine
from validation.evidence_validation_engine import EvidenceValidationEngine
from storage.evidence_store import EvidenceStore


# ==========================================================
# REQUEST-SCOPED EVIDENCE STATE
# ==========================================================
#
# The epistemic store is request-scoped so authenticated users never share
# mutable evidence state through the process-global FastAPI object. Existing
# engines receive this proxy and transparently resolve the store bound to the
# current request context.
# ==========================================================

_evidence_store_context: ContextVar[EvidenceStore | None] = ContextVar(
    "kalatrace_evidence_store",
    default=None,
)


class EvidenceStoreProxy:
    """Delegate EvidenceStore operations to the current request's store."""

    def _store(self) -> EvidenceStore:
        store = _evidence_store_context.get()
        if store is None:
            raise RuntimeError("EvidenceStore não está vinculado à requisição atual.")
        return store

    def __getattr__(self, name):
        return getattr(self._store(), name)


request_evidence_store = EvidenceStoreProxy()

from contracts.iec_contract import IECContract


# ==========================================================
# COMMAND & MISSION CENTER
# ==========================================================

from core.cmc.command_mission_center import CommandMissionCenter



# ==========================================================
# EVENT BUS
# ==========================================================

from core.events.event_bus import EventBus
from core.events.event import Event
from core.events.event_type import EventType
from core.events.event_priority import EventPriority


# ==========================================================
# SECURITY
# ==========================================================

from core.security.security_manager import SecurityManager


# ==========================================================
# INTEGRATIONS
# ==========================================================

from integrations.supabase import SupabaseClient, SupabaseError
from integrations.auth import install_auth_middleware
from core.persistence.request_context import (
    get_persistence_context,
    queue_persistence_event,
    queue_persistence_transition,
    get_pending_persistence_queue,
    clear_persistence_queue,
)
from integrations.neo4j import Neo4jClient
from api.research_forms import router as research_forms_router
from local_agent.sandbox import LocalAgentSandboxError, execute_task_spec
from core.agent_planning.coding_planner import CodingPlanner
from core.evolution_pipeline.governed_cycle import GovernedEvolutionCycle


# ==========================================================
# APPLICATION
# ==========================================================

app = FastAPI(
    title="KALATRACE API",
)


# ==========================================================
# SUPABASE
# ==========================================================

supabase_client = SupabaseClient()

install_auth_middleware(
    app,
    supabase_client,
)


# ==========================================================
# CORS
# ==========================================================

_cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "KALATRACE_CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# NEO4J AURA
# ==========================================================
#
# Neo4j é inicializado depois do load_dotenv().
#
# Variáveis esperadas:
#
#   NEO4J_URI
#   NEO4J_USERNAME
#   NEO4J_PASSWORD
#   NEO4J_DATABASE
#   NEO4J_ENABLED
#
# Nenhuma senha deve ser armazenada neste arquivo.
# ==========================================================

neo4j_client = Neo4jClient()
app.state.supabase = supabase_client
app.state.neo4j = neo4j_client
app.include_router(research_forms_router)


# ==========================================================
# KALATRACE ENGINES
# ==========================================================

engine = CoreEngine()

graph = KnowledgeGraph()

evaluator = Evaluator()

optimizer = Optimizer()

self_model = SelfModel()

observer = Observer(
    self_model
)


# ==========================================================
# ACQUISITION PIPELINE
# ==========================================================

acquisition_pipeline = AcquisitionPipeline()

iec_builder = IECBuilder(
    engine
)


# ==========================================================
# ROBOTICS SKILL
# ==========================================================

robotics_skill = RoboticsSkill()

robotics_skill.activate()

robotics_api = RoboticsAPI(
    robotics_skill
)


# ==========================================================
# EVIDENCE / VALIDATION
# ==========================================================

@app.middleware("http")
async def request_scoped_evidence_store(request: Request, call_next):
    """Bind an isolated mutable EvidenceStore to each HTTP request."""
    token = _evidence_store_context.set(EvidenceStore())
    try:
        return await call_next(request)
    finally:
        _evidence_store_context.reset(token)


# Engines keep a single stable dependency object, but the proxy resolves to
# the isolated EvidenceStore of the current request.
evidence_store = request_evidence_store


def _persist_kee_event(
    iec_id: Optional[str],
    event_type: str,
    details: Dict[str, Any],
) -> None:
    """Persist KEE lifecycle events using the authenticated request context."""
    context = get_persistence_context()
    if context is None:
        return
    queue_persistence_event(iec_id, event_type, details)


def _persist_kee_state_transition(
    iec_id: str,
    from_state: Optional[str],
    to_state: str,
    reason: str,
) -> None:
    """Persist KEE state transitions using the authenticated request context."""
    context = get_persistence_context()
    if context is None:
        return
    queue_persistence_transition(iec_id, from_state, to_state, reason)


def _flush_kee_persistence(request: Request) -> None:
    """Flush queued KEE records only after the parent IEC exists in Supabase."""
    context = get_persistence_context()
    if context is None:
        return
    access_token = context["access_token"]
    user_id = context["user_id"]
    events, transitions = get_pending_persistence_queue()
    for iec_id, from_state, to_state, reason in transitions:
        supabase_client.record_iec_state_transition(
            access_token,
            user_id,
            iec_id,
            from_state,
            to_state,
            reason,
        )
    for iec_id, event_type, details in events:
        supabase_client.record_knowledge_evolution_event(
            access_token,
            user_id,
            iec_id,
            event_type,
            details,
        )
    clear_persistence_queue()


cognitive_orchestrator = CognitiveOrchestrator(
    evidence_store=evidence_store,
    graph=graph,
    event_sink=_persist_kee_event,
    state_transition_sink=_persist_kee_state_transition,
)

structural_validator = ValidationEngine(
    graph,
    evidence_store,
)

evidence_validator = EvidenceValidationEngine(
    evidence_store,
)


# ==========================================================
# PERSISTENT / PROJECT-SCOPED CMC
# ==========================================================

@app.post("/cmc/persistent/missions")
def persist_cmc_mission(payload: CmcMissionPersistIn, request: Request):
    try:
        result = supabase_client.create_cmc_mission(request.state.access_token, request.state.user["id"], payload.model_dump())
        return {"status":"created","mission":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/cmc/persistent/missions")
def list_persistent_cmc_missions(request: Request, project_id: Optional[str] = None, limit: int = 100):
    try: return {"missions": supabase_client.list_cmc_missions(request.state.access_token, project_id, limit)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

# ==========================================================
# COMMAND & MISSION CENTER
# ==========================================================

cmc = CommandMissionCenter()

cmc.connect_robotics(
    robotics_skill
)

cmc.connect_cognitive_orchestrator(
    cognitive_orchestrator
)



# ==========================================================
# EVENT BUS
# ==========================================================

event_bus = EventBus()

event_bus.initialize()


# ==========================================================
# SECURITY MANAGER
# ==========================================================

security_manager = SecurityManager()


# ==========================================================
# AUTHENTICATION MODELS
# ==========================================================

class AuthCredentialsIn(BaseModel):
    email: str
    password: str


class AuthSignupIn(AuthCredentialsIn):
    full_name: Optional[str] = None


# ==========================================================
# AUTHENTICATION ENDPOINTS
# ==========================================================

@app.post("/auth/signup")
def auth_signup(
    payload: AuthSignupIn,
):
    metadata = (
        {"full_name": payload.full_name}
        if payload.full_name
        else {}
    )

    try:
        return supabase_client.sign_up(
            payload.email,
            payload.password,
            metadata,
        )

    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc


@app.post("/auth/login")
def auth_login(
    payload: AuthCredentialsIn,
):
    try:
        return supabase_client.sign_in(
            payload.email,
            payload.password,
        )

    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc


@app.post("/auth/logout")
def auth_logout(
    request: Request,
):
    token = (
        request.state.access_token
        if hasattr(request.state, "access_token")
        else None
    )

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    try:
        supabase_client.sign_out(
            token
        )

    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    return {
        "status": "signed_out"
    }


@app.get("/auth/me")
def auth_me(
    request: Request,
):
    return request.state.user


# ==========================================================
# GENERIC SERIALIZATION
# ==========================================================

def _dc(
    obj: Any,
) -> Any:
    """
    Serializa um objeto de domínio para JSON.

    Ordem:

        1. to_dict()
        2. summary()
        3. próprio valor
    """

    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    if hasattr(obj, "summary"):
        return obj.summary()

    return obj


def _guarded(
    fn,
    *args,
    **kwargs,
):
    """
    Executa uma função de domínio e traduz erros conhecidos
    para respostas HTTP apropriadas.
    """

    try:
        return fn(
            *args,
            **kwargs,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except (
        KeyError,
        RuntimeError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# ==========================================================
# NEO4J SERIALIZATION HELPERS
# ==========================================================

def _neo4j_safe_properties(
    value: Any,
) -> Dict[str, Any]:
    """
    Extrai propriedades simples de um objeto de domínio.

    O Neo4j aceita propriedades escalares e mapas/listas
    compatíveis. Esta função evita enviar objetos Python
    complexos diretamente ao driver.
    """

    if value is None:
        return {}

    if isinstance(value, dict):
        result: Dict[str, Any] = {}

        for key, item in value.items():

            if item is None:
                result[str(key)] = None

            elif isinstance(
                item,
                (
                    str,
                    int,
                    float,
                    bool,
                ),
            ):
                result[str(key)] = item

            elif isinstance(
                item,
                list,
            ):
                safe_list = []

                for element in item:
                    if element is None or isinstance(
                        element,
                        (
                            str,
                            int,
                            float,
                            bool,
                        ),
                    ):
                        safe_list.append(element)

                result[str(key)] = safe_list

            else:
                result[str(key)] = str(item)

        return result

    return {}


def _get_object_id(
    obj: Any,
) -> Optional[str]:
    """
    Obtém um identificador de um nó ou objeto de domínio.
    """

    if obj is None:
        return None

    if isinstance(
        obj,
        str,
    ):
        return obj

    value = getattr(
        obj,
        "id",
        None,
    )

    if value is None:
        return None

    return str(value)


def _persist_iec_to_neo4j(
    iec: Any,
) -> Dict[str, Any]:
    """
    Persiste uma IEC e seu KnowledgeNode associado no Neo4j.

    IEC e KnowledgeNode são entidades distintas.

    Estrutura:

        (:IEC)-[:REPRESENTS]->(:KnowledgeNode)
    """

    if not neo4j_client.enabled:
        return {
            "enabled": False,
            "persisted": False,
        }

    iec_id = _get_object_id(
        iec
    )

    if not iec_id:
        raise RuntimeError(
            "Não foi possível determinar o ID da IEC para persistência no Neo4j."
        )

    content = getattr(
        iec,
        "content",
        "",
    )

    node_type = getattr(
        iec,
        "node_type",
        "Conhecimento",
    )

    # ID estrutural independente da IEC.
    knowledge_node_id = (
        f"knowledge:{iec_id}"
    )

    properties = _neo4j_safe_properties(
        getattr(
            iec,
            "__dict__",
            {},
        )
    )

    # ------------------------------------------------------
    # 1. IEC
    # ------------------------------------------------------

    iec_rows = neo4j_client.execute(
        """
        MERGE (i:IEC {id: $iec_id})

        ON CREATE SET
            i.created_at = datetime()

        SET
            i.content = $content,
            i.node_type = $node_type,
            i.updated_at = datetime()

        RETURN
            i.id AS iec_id
        """,
        {
            "iec_id": iec_id,
            "content": str(content),
            "node_type": str(node_type),
        },
    )

    # ------------------------------------------------------
    # 2. KnowledgeNode
    # ------------------------------------------------------

    knowledge_node = neo4j_client.upsert_knowledge_node(
        node_id=knowledge_node_id,
        node_type=str(node_type),
        label=str(content)[:500],
        description=str(content),
        properties={
            **properties,
            "iec_id": iec_id,
            "origin": "KALATRACE",
        },
    )

    # ------------------------------------------------------
    # 3. Relação IEC -> KnowledgeNode
    # ------------------------------------------------------

    association_rows = neo4j_client.execute(
        """
        MATCH (i:IEC {id: $iec_id})
        MATCH (n:KnowledgeNode {id: $knowledge_node_id})

        MERGE (i)-[r:REPRESENTS]->(n)

        ON CREATE SET
            r.created_at = datetime()

        SET
            r.updated_at = datetime()

        RETURN
            i.id AS iec_id,
            n.id AS knowledge_node_id
        """,
        {
            "iec_id": iec_id,
            "knowledge_node_id": knowledge_node_id,
        },
    )

    return {
        "enabled": True,
        "persisted": True,
        "iec_id": iec_id,
        "knowledge_node_id": knowledge_node_id,
        "iec_rows": len(iec_rows),
        "knowledge_node": knowledge_node,
        "association": (
            association_rows[0]
            if association_rows
            else {}
        ),
    }


def _persist_connections_to_neo4j(
    connections: List[Any],
) -> List[Dict[str, Any]]:
    """
    Persiste as relações semânticas produzidas pela inferência.

    Cada relação liga dois KnowledgeNodes.

    A IEC permanece separada dos nós estruturais.
    """

    if not neo4j_client.enabled:
        return []

    persisted: List[Dict[str, Any]] = []

    for connection in connections:

        if not isinstance(
            connection,
            (
                tuple,
                list,
            ),
        ):
            continue

        if len(connection) < 3:
            continue

        source = connection[0]
        target = connection[1]
        score = connection[2]

        source_id = _get_object_id(
            source
        )

        target_id = _get_object_id(
            target
        )

        if not source_id or not target_id:
            continue

        source_node_id = (
            f"knowledge:{source_id}"
        )

        target_node_id = (
            f"knowledge:{target_id}"
        )

        edge_id = (
            f"{source_node_id}:"
            f"{target_node_id}:"
            f"semantic_relation"
        )

        edge = neo4j_client.upsert_knowledge_edge(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type="semantic_relation",
            properties={
                "score": float(score),
                "source_iec_id": source_id,
                "target_iec_id": target_id,
            },
        )

        persisted.append(
            {
                "edge_id": edge_id,
                "source_iec_id": source_id,
                "target_iec_id": target_id,
                "score": float(score),
                "neo4j": edge,
            }
        )

    return persisted


def _persist_graph_to_neo4j(
    iec: Any,
    connections: List[Any],
) -> Dict[str, Any]:
    """
    Persiste uma unidade completa do Knowledge Graph.

    Ordem:

        1. IEC
        2. KnowledgeNode
        3. relação IEC -> KnowledgeNode
        4. KnowledgeEdges
    """

    if not neo4j_client.enabled:
        return {
            "enabled": False,
            "persisted": False,
            "edges_persisted": 0,
        }

    iec_result = _persist_iec_to_neo4j(
        iec
    )

    edge_results = _persist_connections_to_neo4j(
        connections
    )

    return {
        **iec_result,
        "edges_persisted": len(
            edge_results
        ),
        "edges": edge_results,
    }


# ==========================================================
# IEC INGESTION
# ==========================================================

def _ingest_iec(
    iec: Any,
) -> Dict[str, Any]:
    """
    Insere uma IEC no KnowledgeGraph local e executa:

        1. inferência
        2. governança
        3. evolução
        4. observabilidade
        5. persistência no Neo4j

    Este fluxo é compartilhado por:

        POST /iec
        POST /acquisition/search-and-build
        POST /acquisition/build-iecs
    """

    # ------------------------------------------------------
    # LOCAL KNOWLEDGE GRAPH
    # ------------------------------------------------------

    graph.add_node(
        iec
    )

    threshold = (
        0.3
        if is_using_fallback()
        else 0.55
    )

    connections = infer(
        graph,
        iec,
        threshold=threshold,
    )

    # ------------------------------------------------------
    # LOCAL EDGES
    # ------------------------------------------------------

    for source, target, score in connections:

        graph.add_edge(
            source,
            target,
            "semantic_relation",
            score,
        )

    # ------------------------------------------------------
    # GOVERNANCE
    # ------------------------------------------------------

    evaluator.filter_edges(
        graph,
        min_score=(
            0.15
            if is_using_fallback()
            else 0.4
        ),
    )

    # ------------------------------------------------------
    # EVOLUTION
    # ------------------------------------------------------

    optimizer.reinforce_edges(
        graph
    )

    optimizer.prune_graph(
        graph,
        threshold=0.1,
    )

    # ------------------------------------------------------
    # METACOGNITION
    # ------------------------------------------------------

    report = observer.monitor_cycle(
        graph,
        connections,
    )

    # ------------------------------------------------------
    # NEO4J PERSISTENCE
    # ------------------------------------------------------

    neo4j_persistence = _persist_graph_to_neo4j(
        iec,
        connections,
    )

    return {
        "iec": iec.id,
        "connections": connections,
        "metacognition": report,
        "neo4j": neo4j_persistence,
    }


# ==========================================================
# IEC
# ==========================================================

class IECIn(BaseModel):
    id: str
    content: str
    node_type: str = "Conhecimento"


@app.post("/iec")
def create_iec(
    payload: IECIn,
    request: Request,
):
    iec = engine.create_iec(
        payload.id,
        payload.content,
        node_type=payload.node_type,
    )

    try:
        result = _ingest_iec(
            iec
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha durante a ingestão/persistência "
                f"da IEC no Knowledge Graph: {exc}"
            ),
        ) from exc

    persisted = supabase_client.persist_iec(
        request.state.access_token,
        request.state.user["id"],
        iec,
    )

    return {
        "status": "created",
        **result,
        "using_fallback_embedding": (
            is_using_fallback()
        ),
        "persistence": {
            "supabase": True,
            "neo4j": bool(
                result.get(
                    "neo4j",
                    {},
                ).get(
                    "persisted",
                    False,
                )
            ),
            "iec_rows": (
                len(persisted)
                if isinstance(
                    persisted,
                    list,
                )
                else 1
            ),
        },
    }


# ==========================================================
# GRAPH
# ==========================================================

@app.get("/graph")
def get_graph():
    return {
        "nodes": {
            nid: {
                "content": getattr(node, "content", None),
                "node_type": getattr(node, "node_type", node.__class__.__name__),
            }
            for nid, node in graph.nodes.items()
        },
        "knowledge_nodes": {
            nid: node.to_dict()
            for nid, node in graph.knowledge_nodes.items()
        },
        "edges": graph.edges,
    }


# ==========================================================
# PERSISTENCE HEALTH / CROSS-STORE CONSISTENCY
# ==========================================================

@app.post("/persistence/sync/iec/{iec_id}")
def sync_iec_to_neo4j(iec_id: str, request: Request):
    """Synchronize one Supabase IEC into Neo4j and persist the sync ledger."""
    try:
        rows = supabase_client.get_iec(request.state.access_token, iec_id)
        row = rows[0] if isinstance(rows, list) and rows else None
        if not row:
            raise HTTPException(status_code=404, detail="IEC not found in Supabase")
        from types import SimpleNamespace
        iec = SimpleNamespace(
            id=str(row["id"]),
            content=row.get("statement", ""),
            node_type=(row.get("methodology") or {}).get("node_type", "Conhecimento"),
            metadata=(row.get("result") or {}).get("metadata", {}),
        )
        try:
            current = supabase_client.list_knowledge_sync_status(request.state.access_token, iec_id, 1)
            attempts = int(current[0].get("attempts", 0)) + 1 if current else 1
        except Exception:
            attempts = 1
        try:
            neo = _persist_graph_to_neo4j(iec, [])
            status = "synced" if neo.get("persisted") else "failed"
            sync = supabase_client.upsert_knowledge_sync_status(request.state.access_token, request.state.user["id"], iec_id, f"knowledge:{iec_id}", status, attempts, None if status == "synced" else "Neo4j did not persist", {"neo4j": neo})
            return {"status": status, "iec_id": iec_id, "neo4j": neo, "sync": sync}
        except Exception as exc:
            supabase_client.upsert_knowledge_sync_status(request.state.access_token, request.state.user["id"], iec_id, f"knowledge:{iec_id}", "failed", attempts, str(exc))
            raise HTTPException(status_code=503, detail=f"Neo4j synchronization failed: {exc}") from exc
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.get("/persistence/sync")
def list_knowledge_sync(request: Request, iec_id: Optional[str] = None):
    try:
        return {"sync": supabase_client.list_knowledge_sync_status(request.state.access_token, iec_id)}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.get("/persistence/health")
def get_persistence_health(request: Request):
    """Verifica as duas persistências sem criar dependência direta entre os bancos.

    Supabase/Postgres é a fonte transacional; Neo4j é a projeção de grafo.
    A API é a camada de orquestração entre eles.
    """
    result = {"supabase": {"connected": False}, "neo4j": {"connected": False}, "architecture": {"source_of_truth": "supabase_postgres", "graph_projection": "neo4j"}}
    try:
        forms = supabase_client.select("research_form_records", request.state.access_token, select="id", filters={"limit": "1"})
        result["supabase"] = {"connected": True, "research_form_records_accessible": True, "sample_rows": len(forms) if isinstance(forms, list) else 0}
    except Exception as exc:
        result["supabase"] = {"connected": False, "error": str(exc)}
    try:
        result["neo4j"] = neo4j_client.verify_connectivity()
    except Exception as exc:
        result["neo4j"] = {"connected": False, "error": str(exc)}
    result["healthy"] = bool(result["supabase"].get("connected")) and bool(result["neo4j"].get("connected"))
    return result


# ==========================================================
# PROJECTS / LOCAL AGENT CONTROL PLANE
# ==========================================================

class ProjectCreateIn(BaseModel):
    slug: str
    name: str
    project_type: str = "custom"
    domain: Optional[str] = None
    description: Optional[str] = None
    status: str = "development"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdateIn(BaseModel):
    name: Optional[str] = None
    project_type: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CmcMissionPersistIn(BaseModel):
    project_id: Optional[str] = None
    name: str
    objective: str
    priority: str = "NORMAL"
    status: str = "CREATED"
    payload: Dict[str, Any] = Field(default_factory=dict)


class AgentTaskIn(BaseModel):
    project_id: str
    title: str
    description: str = ""
    priority: int = Field(default=50, ge=0, le=100)
    task_type: str = "improvement"
    execution_spec: Dict[str, Any] = Field(default_factory=dict)


class AgentPlanIn(BaseModel):
    project_id: str
    title: Optional[str] = None
    description: str = ""
    priority: int = Field(default=50, ge=0, le=100)


class AgentExplicitPlanIn(BaseModel):
    project_id: str
    title: str
    description: str = ""
    priority: int = Field(default=50, ge=0, le=100)
    mission_id: Optional[str] = None
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    post_checks: List[Dict[str, Any]] = Field(default_factory=lambda: [{"operation": "pytest", "args": ["-q"]}, {"operation": "compileall"}])

@app.get("/workspace/me")
def workspace_me(request: Request):
    user = request.state.user
    return {"user": user, "role": "owner", "workspace": {"name": user.get("user_metadata", {}).get("full_name") or user.get("email", "Workspace")}}

@app.get("/projects")
def list_projects(request: Request):
    try: return {"projects": supabase_client.list_projects(request.state.access_token)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/projects")
def create_project(payload: ProjectCreateIn, request: Request):
    slug = payload.slug.strip().lower().replace(" ", "-")
    if not slug or not payload.name.strip(): raise HTTPException(status_code=400, detail="Project slug and name are required")
    try:
        result = supabase_client.create_project(request.state.access_token, request.state.user["id"], {"slug": slug, "name": payload.name.strip(), "project_type": payload.project_type, "domain": payload.domain, "description": payload.description, "status": payload.status, "metadata": payload.metadata})
        return {"status": "created", "project": result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.patch("/projects/{project_id}")
def update_project(project_id: str, payload: ProjectUpdateIn, request: Request):
    values = {k:v for k,v in payload.model_dump(exclude_none=True).items()}
    if not values: raise HTTPException(status_code=400, detail="No project fields supplied")
    try:
        result=supabase_client.update_project(request.state.access_token, project_id, values)
        return {"status":"updated","project":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.delete("/projects/{project_id}")
def delete_project(project_id: str, request: Request):
    try:
        result=supabase_client.delete_project(request.state.access_token, project_id)
        return {"status":"deleted","project":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/projects/{project_id}/members")
def project_members(project_id: str, request: Request):
    try: return {"members": supabase_client.list_project_memberships(request.state.access_token, project_id)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/agent/status")
def local_agent_status(request: Request):
    try:
        tasks=supabase_client.list_agent_tasks(request.state.access_token, limit=100)
        queued=[t for t in tasks if t.get("status") in {"queued","approved","running"}] if isinstance(tasks,list) else []
        instances = supabase_client.list_agent_instances(request.state.access_token)
        online = [i for i in (instances or []) if i.get("status") in {"online", "busy"}] if isinstance(instances, list) else []
        return {"control_plane":"ready","local_agent_process":"connected" if online else "not_connected","message":"Executor local conectado." if online else "O painel está pronto; o executor local ainda não está conectado.","queued_tasks":len(queued),"online_instances":len(online)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/agent/tasks")
def list_agent_tasks(request: Request, project_id: Optional[str] = None, limit: int = 100):
    try: return {"tasks": supabase_client.list_agent_tasks(request.state.access_token, project_id, limit)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/agent/tasks")
def create_agent_task(payload: AgentTaskIn, request: Request):
    try:
        result=supabase_client.persist_agent_task(request.state.access_token, request.state.user["id"], payload.project_id, payload.title, payload.description, payload.priority, payload.task_type, payload.execution_spec)
        return {"status":"queued","task":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/agent/tasks/plan")
def plan_agent_task(payload: AgentPlanIn, request: Request):
    """Create a durable planning task. Planning never grants execution authority."""
    mission_id = f"planning-{request.state.user['id']}"
    plan = CodingPlanner().plan(mission_id, payload.description or payload.title or "Improve the project")
    try:
        result = supabase_client.persist_agent_task(
            request.state.access_token,
            request.state.user["id"],
            payload.project_id,
            payload.title or "Coding Agent plan",
            payload.description,
            payload.priority,
            "coding_plan",
            plan.execution_spec,
            plan=plan.to_dict(),
        )
        return {"status": "planning", "plan": plan.to_dict(), "task": result[0] if isinstance(result, list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.post("/agent/tasks/explicit-plan")
def create_explicit_agent_plan(payload: AgentExplicitPlanIn, request: Request):
    """Persist a concrete proposed coding change set for later human approval."""
    if not payload.operations:
        raise HTTPException(status_code=400, detail="At least one explicit file operation is required")
    spec = {"operation": "code_apply", "operations": payload.operations, "post_checks": payload.post_checks, "auto_rollback": True}
    try:
        CodingPlanner.validate_execution_spec(spec)
        mission_id = payload.mission_id or f"planning-{request.state.user['id']}"
        plan = CodingPlanner().plan(mission_id, payload.title, None).to_dict()
        plan["execution_spec"] = spec
        result = supabase_client.persist_agent_task(
            request.state.access_token, request.state.user["id"], payload.project_id,
            payload.title, payload.description, payload.priority, "coding", spec,
            mission_id=payload.mission_id, plan=plan,
        )
        return {"status": "planning", "approval_required": True, "plan": plan, "task": result[0] if isinstance(result, list) and result else result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.patch("/agent/tasks/{task_id}")
def update_agent_task(task_id: str, payload: Dict[str, Any], request: Request):
    values={k:v for k,v in payload.items() if k in {"status","priority","title","description","result","started_at","completed_at","execution_spec","execution_log","approved_by","approved_at"}}
    if not values: raise HTTPException(status_code=400, detail="No mutable task fields supplied")
    try:
        result=supabase_client.update_agent_task(request.state.access_token, task_id, values)
        return {"status":"updated","task":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/agent/tasks/{task_id}/approve")
def approve_agent_task(task_id: str, request: Request):
    try:
        tasks = supabase_client.list_agent_tasks(request.state.access_token, limit=500)
        task = next((item for item in (tasks or []) if item.get("id") == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.get("status") not in {"queued", "planning"}:
            raise HTTPException(status_code=409, detail="Only queued/planning tasks can be approved")
        from datetime import datetime, timezone
        result=supabase_client.update_agent_task(request.state.access_token, task_id, {
            "status":"approved",
            "approved_by": request.state.user["id"],
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "execution_log": [*(task.get("execution_log") or []), {"event":"approved", "by":request.state.user["id"], "at":datetime.now(timezone.utc).isoformat()}],
        })
        return {"status":"approved","task":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def get_health():
    return compute_system_health(
        graph,
        self_model,
    )


# ==========================================================
# NEO4J HEALTH
# ==========================================================

@app.get("/neo4j/health")
def get_neo4j_health():
    """
    Verifica a conectividade do KALATRACE com o Neo4j Aura.
    """

    try:
        return neo4j_client.verify_connectivity()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Neo4j connection failed: "
                f"{exc}"
            ),
        ) from exc


# ==========================================================
# NEO4J GRAPH STATS
# ==========================================================

@app.get("/neo4j/stats")
def get_neo4j_stats():
    """
    Retorna estatísticas do Knowledge Graph persistido
    no Neo4j Aura.
    """

    if not neo4j_client.enabled:
        return {
            "enabled": False,
            "nodes": 0,
            "knowledge_nodes": 0,
            "iecs": 0,
            "edges": 0,
        }

    try:
        rows = neo4j_client.execute(
            """
            OPTIONAL MATCH (n:KnowledgeNode)
            WITH count(n) AS knowledge_nodes

            OPTIONAL MATCH (i:IEC)
            WITH
                knowledge_nodes,
                count(i) AS iecs

            OPTIONAL MATCH ()-[r:KNOWLEDGE_EDGE]->()
            RETURN
                knowledge_nodes,
                iecs,
                count(r) AS edges
            """
        )

        if not rows:
            return {
                "enabled": True,
                "nodes": 0,
                "knowledge_nodes": 0,
                "iecs": 0,
                "edges": 0,
            }

        row = rows[0]

        return {
            "enabled": True,
            "nodes": (
                int(row.get("knowledge_nodes", 0))
                + int(row.get("iecs", 0))
            ),
            "knowledge_nodes": int(
                row.get(
                    "knowledge_nodes",
                    0,
                )
            ),
            "iecs": int(
                row.get(
                    "iecs",
                    0,
                )
            ),
            "edges": int(
                row.get(
                    "edges",
                    0,
                )
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha ao consultar estatísticas "
                f"do Neo4j: {exc}"
            ),
        ) from exc


# ==========================================================
# NEO4J KNOWLEDGE GRAPH
# ==========================================================

@app.get("/neo4j/graph")
def get_neo4j_graph():
    """
    Retorna o Knowledge Graph persistido no Neo4j.

    Este endpoint consulta diretamente o banco online,
    não o grafo local em memória.
    """

    if not neo4j_client.enabled:
        return {
            "enabled": False,
            "nodes": [],
            "edges": [],
        }

    try:

        nodes = neo4j_client.execute(
            """
            MATCH (n)
            WHERE n:KnowledgeNode OR n:IEC
            RETURN
                labels(n) AS labels,
                n {.*} AS properties
            ORDER BY properties.id
            """
        )

        edges = neo4j_client.execute(
            """
            MATCH (source)-[r:KNOWLEDGE_EDGE]->(target)
            RETURN
                source.id AS source_id,
                target.id AS target_id,
                r.id AS edge_id,
                r.edge_type AS edge_type,
                r.score AS score,
                r.properties AS properties
            ORDER BY r.id
            """
        )

        return {
            "enabled": True,
            "nodes": nodes,
            "edges": edges,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha ao consultar o Knowledge Graph "
                f"no Neo4j: {exc}"
            ),
        ) from exc


# ==========================================================
# CURATION
# ==========================================================

@app.get("/curation/gaps")
def get_gaps():
    return detect_gaps(
        graph
    )


@app.get("/curation/duplicates")
def get_duplicates():
    return detect_duplicates(
        graph
    )


@app.get("/curation/conflicts")
def get_conflicts():
    return detect_conflicts(
        graph
    )


# ==========================================================
# COGNITIVE ORCHESTRATOR
# ==========================================================

class CognitiveCycleIn(BaseModel):
    statement: str
    submitted_by: str
    submission_type: str = "observacao"
    inference_threshold: float = 0.55


def _serialize_cycle_result(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Serializa o IEC retornado pelo CognitiveOrchestrator.
    """

    serialized = dict(
        result
    )

    iec = serialized.get(
        "iec"
    )

    serialized["iec"] = (
        {
            "id": getattr(
                iec,
                "id",
                None,
            ),
            "content": getattr(
                iec,
                "content",
                None,
            ),
            "node_type": getattr(
                iec,
                "node_type",
                None,
            ),
        }
        if iec is not None
        else None
    )

    return serialized


@app.post("/cognitive-cycle/run")
def run_cognitive_cycle(
    payload: CognitiveCycleIn,
    request: Request,
):
    result = cognitive_orchestrator.run_cycle(
        statement=payload.statement,
        submitted_by=payload.submitted_by,
        submission_type=payload.submission_type,
        inference_threshold=payload.inference_threshold,
    )

    iec = result.get("iec") if isinstance(result, dict) else None
    persistence = {"supabase": False, "neo4j": False}
    if iec is not None:
        try:
            supabase_client.persist_iec(
                request.state.access_token,
                request.state.user["id"],
                iec,
            )
            _flush_kee_persistence(request)
            persistence["supabase"] = True
        except SupabaseError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        try:
            neo = _persist_graph_to_neo4j(
                iec,
                result.get("connections", []) if isinstance(result, dict) else [],
            )
            persistence["neo4j"] = bool(neo.get("persisted"))
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Falha ao sincronizar ciclo com Neo4j: {exc}") from exc

    serialized = _serialize_cycle_result(result)
    serialized["persistence"] = persistence
    return serialized


@app.get("/cognitive-cycle/active")
def list_active_cognitive_cycles():
    return cognitive_orchestrator.list_active_cycles()


@app.get("/cognitive-cycle/stats")
def get_cognitive_cycle_stats():
    return cognitive_orchestrator.stats()


@app.get("/cognitive-cycle/workflow")
def get_cognitive_cycle_workflow():
    return cognitive_orchestrator.workflow_definition()


@app.get("/cognitive-cycle/strategic-plan")
def get_cognitive_cycle_strategic_plan():
    return cognitive_orchestrator.build_strategic_plan()


@app.get("/cognitive-cycle/health")
def get_cognitive_cycle_health():
    return cognitive_orchestrator.health_check()


@app.get("/cognitive-cycle/{iec_id}")
def get_cognitive_cycle_state(
    iec_id: str,
):
    try:
        return cognitive_orchestrator.get_cycle_state(
            iec_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# ==========================================================
# ACQUISITION
# ==========================================================

class AcquisitionSearchIn(BaseModel):
    query: str
    max_results_per_source: int = 20
    resolve_duplicates: bool = True


@app.post("/acquisition/search")
def search_acquisition(
    payload: AcquisitionSearchIn,
):
    return acquisition_pipeline.run(
        query=payload.query,
        max_results_per_source=payload.max_results_per_source,
        resolve_duplicates=payload.resolve_duplicates,
    )


@app.get("/acquisition/stats")
def get_acquisition_stats():
    return acquisition_pipeline.stats()


@app.get("/acquisition/health")
def get_acquisition_health():
    return acquisition_pipeline.health_check()


class AcquisitionSearchAndBuildIn(BaseModel):
    query: str
    max_results_per_source: int = 20
    resolve_duplicates: bool = True
    node_type: str = "Literatura Científica"


class AcquisitionBuildIn(BaseModel):
    records: List[Dict[str, Any]]
    node_type: str = "Literatura Científica"


@app.post("/acquisition/search-and-build")
def search_and_build_acquisition(
    payload: AcquisitionSearchAndBuildIn,
):
    search_result = acquisition_pipeline.run(
        query=payload.query,
        max_results_per_source=payload.max_results_per_source,
        resolve_duplicates=payload.resolve_duplicates,
    )

    skipped_before = len(
        iec_builder.skipped
    )

    iecs = iec_builder.build_many_from_acquisition(
        search_result["records"],
        node_type=payload.node_type,
        graph=graph,
    )

    skipped_this_call = (
        iec_builder.skipped[
            skipped_before:
        ]
    )

    try:
        ingested = [
            _ingest_iec(
                iec
            )
            for iec in iecs
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha durante a ingestão da aquisição "
                f"no Knowledge Graph: {exc}"
            ),
        ) from exc

    return {
        "query": payload.query,
        "sources_queried": search_result[
            "sources_queried"
        ],
        "sources_failed": search_result[
            "sources_failed"
        ],
        "records_retrieved": search_result[
            "total_retrieved"
        ],
        "records_after_dedup": search_result[
            "total_after_dedup"
        ],
        "iecs_created": len(
            iecs
        ),
        "iecs_skipped": skipped_this_call,
        "ingested": ingested,
    }


@app.post("/acquisition/build-iecs")
def build_iecs_from_records(
    payload: AcquisitionBuildIn,
):
    skipped_before = len(
        iec_builder.skipped
    )

    iecs = iec_builder.build_many_from_acquisition(
        payload.records,
        node_type=payload.node_type,
        graph=graph,
    )

    skipped_this_call = (
        iec_builder.skipped[
            skipped_before:
        ]
    )

    try:
        ingested = [
            _ingest_iec(
                iec
            )
            for iec in iecs
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha durante a persistência "
                f"da aquisição no Neo4j: {exc}"
            ),
        ) from exc

    return {
        "records_received": len(
            payload.records
        ),
        "iecs_created": len(
            iecs
        ),
        "iecs_skipped": skipped_this_call,
        "ingested": ingested,
    }


@app.get("/acquisition/build-stats")
def get_acquisition_build_stats():
    return iec_builder.stats()


# ==========================================================
# ROBOTICS
# ==========================================================

class RobotConnectIn(BaseModel):
    robot_id: str
    metadata: Optional[Dict[str, Any]] = None


class RobotIdIn(BaseModel):
    robot_id: str


class RobotSensorIn(BaseModel):
    robot_id: str
    sensor: str
    value: Any


class RobotMissionStartIn(BaseModel):
    robot_id: str
    mission: str


class RobotMissionCompleteIn(BaseModel):
    robot_id: str
    mission: str
    result: Any = None


class RobotObjectDetectedIn(BaseModel):
    robot_id: str
    object_name: str
    confidence: float


class RobotErrorIn(BaseModel):
    robot_id: str
    error: str


@app.post("/robotics/connect")
def connect_robot(
    payload: RobotConnectIn,
):
    return robotics_api.connect_robot(
        payload.robot_id,
        payload.metadata,
    )


@app.post("/robotics/disconnect")
def disconnect_robot(
    payload: RobotIdIn,
):
    return robotics_api.disconnect_robot(
        payload.robot_id
    )


@app.post("/robotics/sensor")
def update_robot_sensor(
    payload: RobotSensorIn,
):
    return robotics_api.update_sensor(
        payload.robot_id,
        payload.sensor,
        payload.value,
    )


@app.post("/robotics/mission/start")
def start_robot_mission(
    payload: RobotMissionStartIn,
):
    return robotics_api.start_mission(
        payload.robot_id,
        payload.mission,
    )


@app.post("/robotics/mission/complete")
def complete_robot_mission(
    payload: RobotMissionCompleteIn,
):
    return robotics_api.complete_mission(
        payload.robot_id,
        payload.mission,
        payload.result,
    )


@app.post("/robotics/object-detected")
def report_robot_object_detected(
    payload: RobotObjectDetectedIn,
):
    return robotics_api.detect_object(
        payload.robot_id,
        payload.object_name,
        payload.confidence,
    )


@app.post("/robotics/error")
def report_robot_error(
    payload: RobotErrorIn,
):
    return robotics_api.report_error(
        payload.robot_id,
        payload.error,
    )


@app.get("/robotics/status")
def get_robotics_status():
    return robotics_api.get_status()


@app.get("/robotics/{robot_id}")
def get_robot(
    robot_id: str,
):
    context = robotics_api.get_robot(
        robot_id
    )

    if context is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Robô não encontrado: {robot_id}"
            ),
        )

    return context


# ==========================================================
# STRUCTURAL VALIDATION
# ==========================================================

@app.post("/validation/iec/{iec_id}")
def validate_iec_structural(
    iec_id: str,
):
    result = structural_validator.validate_iec(
        iec_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"IEC não encontrada no grafo: {iec_id}"
            ),
        )

    return result


@app.post("/validation/all")
def validate_all_structural():
    return structural_validator.validate_all()


@app.get("/validation/weak")
def get_weak_knowledge(
    threshold: float = 0.3,
):
    return [
        _dc(node)
        for node in structural_validator.weak_knowledge(
            threshold=threshold
        )
    ]


@app.get("/validation/conflicts")
def get_structural_conflicts():
    return structural_validator.detect_basic_conflicts()


@app.get("/validation/report")
def get_structural_report():
    return structural_validator.report()


@app.get("/validation/history")
def get_structural_validation_history():
    return structural_validator.get_validation_history()


@app.get("/validation/stats")
def get_structural_validation_stats():
    return structural_validator.stats()


# ==========================================================
# EVIDENCE STORE
# ==========================================================

class EvidenceCreateIn(BaseModel):
    evidence_id: str
    source: str
    evidence_type: str
    title: str
    description: str
    confidence: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class EvidenceLinkIn(BaseModel):
    evidence_id: str
    iec_id: str
    relation: str = "SUPPORTS"
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceConfidenceIn(BaseModel):
    confidence: float
    reason: str


def _hydrate_iec_from_supabase(request: Request, iec_id: str) -> Any:
    """Reconstrói uma IEC persistida quando ela não está no grafo local."""
    iec = graph.get_node(iec_id)
    if iec is not None:
        return iec

    try:
        rows = supabase_client.get_iec(
            request.state.access_token,
            iec_id,
        )
    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    if not rows:
        return None

    row = rows[0]
    methodology = row.get("methodology") or {}
    result = row.get("result") or {}
    statement = row.get("statement") or ""

    restored = SimpleNamespace(
        id=row.get("id") or iec_id,
        title=row.get("name") or iec_id,
        content=statement,
        statement=statement,
        node_type=methodology.get("knowledge_type", "Conhecimento"),
        knowledge_type=methodology.get("knowledge_type", "Conhecimento"),
        confidence=float(result.get("confidence", 0.0) or 0.0),
        status=result.get("status", "active"),
        evidence_ids=result.get("evidence_ids", []) or [],
        metadata=result.get("metadata", {}) or {},
    )
    graph.add_node(restored)
    return restored


def _hydrate_evidence_store_from_supabase(request: Request) -> Dict[str, int]:
    """Reconstrói o EvidenceStore do usuário autenticado antes de consultas epistemológicas."""
    try:
        evidence_rows = supabase_client.list_evidence(
            request.state.access_token,
            limit=500,
        )
        link_rows = supabase_client.list_evidence_iec_links(
            request.state.access_token,
            limit=500,
        )
        return evidence_store.hydrate_from_persistence(
            evidence_rows or [],
            link_rows or [],
        )
    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc


@app.post("/evidence")
def create_evidence(
    payload: EvidenceCreateIn,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    try:
        evidence = evidence_store.create_evidence(
            evidence_id=payload.evidence_id,
            source=payload.source,
            evidence_type=payload.evidence_type,
            title=payload.title,
            description=payload.description,
            confidence=payload.confidence,
            metadata=payload.metadata,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    persisted = supabase_client.persist_evidence(
        request.state.access_token,
        request.state.user["id"],
        evidence,
    )

    return {
        **evidence.to_dict(),
        "persistence": {
            "supabase": True,
            "rows": (
                len(persisted)
                if isinstance(
                    persisted,
                    list,
                )
                else 1
            ),
        },
    }


@app.get("/evidence/{evidence_id}")
def get_evidence(
    evidence_id: str,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    evidence = evidence_store.get_evidence(
        evidence_id
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Evidência não encontrada: "
                f"{evidence_id}"
            ),
        )

    return evidence.to_dict()


@app.delete("/evidence/{evidence_id}")
def delete_evidence(
    evidence_id: str,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    removed = evidence_store.remove_evidence(
        evidence_id
    )

    if removed:
        try:
            supabase_client.delete(
                "evidence_iec_links",
                request.state.access_token,
                {"evidence_id": f"eq.{evidence_id}"},
            )
            supabase_client.delete(
                "evidence",
                request.state.access_token,
                {"id": f"eq.{evidence_id}"},
            )
        except SupabaseError as exc:
            raise HTTPException(
                status_code=exc.status_code,
                detail=str(exc),
            ) from exc

    return {
        "evidence_id": evidence_id,
        "removed": removed,
        "persistence": {"supabase": bool(removed)},
    }


@app.patch("/evidence/{evidence_id}/confidence")
def update_evidence_confidence(
    evidence_id: str,
    payload: EvidenceConfidenceIn,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    evidence_before = evidence_store.get_evidence(evidence_id)
    if evidence_before is None:
        raise HTTPException(
            status_code=404,
            detail=f"Evidência não encontrada: {evidence_id}",
        )
    previous_confidence = evidence_before.confidence

    _guarded(
        evidence_store.update_evidence_confidence,
        evidence_id,
        payload.confidence,
        payload.reason,
    )

    evidence = evidence_store.get_evidence(
        evidence_id
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Evidência não encontrada: "
                f"{evidence_id}"
            ),
        )

    try:
        persisted = supabase_client.persist_evidence(
            request.state.access_token,
            request.state.user["id"],
            evidence,
        )
        supabase_client.record_evidence_history(
            request.state.access_token,
            request.state.user["id"],
            evidence_id,
            "confidence_updated",
            previous_confidence=previous_confidence,
            new_confidence=evidence.confidence,
            reason=payload.reason,
            payload={"source": "api"},
        )
    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    return {
        **evidence.to_dict(),
        "persistence": {
            "supabase": True,
            "rows": len(persisted) if isinstance(persisted, list) else 1,
        },
    }


@app.post("/evidence/link")
def link_evidence_to_iec(
    payload: EvidenceLinkIn,
    request: Request,
):
    relation = payload.relation.upper().strip()

    if relation not in {"SUPPORTS", "CONTRADICTS", "NEUTRAL"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "relation inválida. Use SUPPORTS, "
                "CONTRADICTS ou NEUTRAL."
            ),
        )

    _hydrate_evidence_store_from_supabase(request)

    result = _guarded(
        evidence_store.link_to_iec,
        payload.evidence_id,
        payload.iec_id,
        relation,
        payload.weight,
        payload.reason,
        payload.metadata,
    )

    try:
        persisted = supabase_client.link_evidence_to_iec(
            request.state.access_token,
            request.state.user["id"],
            payload.evidence_id,
            payload.iec_id,
            relation,
            payload.weight,
            payload.reason,
            payload.metadata,
        )
    except SupabaseError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc

    return {
        "evidence_id": payload.evidence_id,
        "iec_id": payload.iec_id,
        "linked": True,
        "relation": relation,
        "weight": payload.weight,
        "reason": payload.reason,
        "metadata": payload.metadata,
        "epistemic_relation": result,
        "persistence": {
            "supabase": True,
            "rows": len(persisted) if isinstance(persisted, list) else 1,
        },
    }


@app.get("/evidence/for-iec/{iec_id}")
def get_evidence_for_iec(
    iec_id: str,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    return [
        evidence.to_dict()
        for evidence in evidence_store.get_evidence_for_iec(
            iec_id
        )
    ]


@app.get("/evidence/strength/{iec_id}")
def get_evidence_strength(
    iec_id: str,
    request: Request,
):
    _hydrate_evidence_store_from_supabase(request)
    return {
        "iec_id": iec_id,
        "evidence_strength": (
            evidence_store.compute_evidence_strength(
                iec_id
            )
        ),
    }


# ==========================================================
# EPISTEMIC CONCLUSION VIEW
# ==========================================================

@app.get("/epistemic/iec/{iec_id}")
def get_epistemic_conclusion(iec_id: str, request: Request):
    """Returns the current epistemic state of one IEC with its evidence trail.

    This projection explains the current support state; it does not declare
    scientific truth.
    """
    _hydrate_evidence_store_from_supabase(request)
    iec = _hydrate_iec_from_supabase(request, iec_id)
    if iec is None:
        raise HTTPException(status_code=404, detail=f"IEC não encontrada: {iec_id}")

    ref = IECRefIn(
        iec_id=iec_id,
        title=getattr(iec, "title", None) or str(getattr(iec, "content", iec_id))[:120],
        statement=getattr(iec, "statement", None) or getattr(iec, "content", ""),
        knowledge_type=getattr(iec, "knowledge_type", None) or getattr(iec, "node_type", "Conhecimento"),
        confidence=float(getattr(iec, "confidence", 0.0) or 0.0),
    )
    contract = _to_iec_contract(ref)
    validation = evidence_validator.validate_iec(contract)
    gaps = evidence_validator.analyze_evidence_gaps(contract)
    synthesis = evidence_store.compute_epistemic_synthesis(iec_id)

    # A projeção mantém a evidência completa e, além disso,
    # explicita o papel epistemológico de cada evidência diante da IEC.
    evidence_by_id = {
        evidence.evidence_id: evidence
        for evidence in evidence_store.get_evidence_for_iec(iec_id)
    }

    epistemic_evidence = []
    for relation in synthesis["relations"]:
        evidence = evidence_by_id.get(relation["evidence_id"])
        if evidence is None:
            continue

        item = evidence.to_dict()
        item["epistemic_relation"] = {
            "id": relation["id"],
            "relation": relation["relation"],
            "weight": relation["weight"],
            "reason": relation["reason"],
            "created_at": relation["created_at"],
            "validated_at": relation["validated_at"],
            "metadata": relation.get("metadata", {}),
        }
        epistemic_evidence.append(item)

    epistemic_evidence.sort(
        key=lambda item: float(item.get("confidence") or 0),
        reverse=True,
    )

    supporting_evidence = [
        item
        for item in epistemic_evidence
        if item["epistemic_relation"]["relation"] == "SUPPORTS"
    ]
    contradicting_evidence = [
        item
        for item in epistemic_evidence
        if item["epistemic_relation"]["relation"] == "CONTRADICTS"
    ]

    support_score = synthesis["support_score"]
    contradiction_score = synthesis["contradiction_score"]

    if contradicting_evidence:
        interpretation = (
            f'{evidence_validator._interpret_strength(validation["classification"])} '
            "Há evidência de divergência registrada separadamente."
        )
    else:
        interpretation = evidence_validator._interpret_strength(
            validation["classification"]
        )

    return {
        "iec": {
            "id": iec_id,
            "title": ref.title,
            "statement": ref.statement,
            "knowledge_type": ref.knowledge_type,
        },
        "current_state": {
            "classification": validation["classification"],
            "evidence_strength": validation["evidence_strength"],
            "support_score": support_score,
            "contradiction_score": contradiction_score,
            "evidence_count": synthesis["evidence_count"],
            "supporting_count": synthesis["supporting_count"],
            "contradicting_count": synthesis["contradicting_count"],
            "neutral_count": synthesis["neutral_count"],
            "graph_confidence": ref.confidence,
            "interpretation": interpretation,
        },
        "synthesis": {
            "support_score": support_score,
            "contradiction_score": contradiction_score,
            "supporting_count": synthesis["supporting_count"],
            "contradicting_count": synthesis["contradicting_count"],
            "neutral_count": synthesis["neutral_count"],
        },
        "evidence": epistemic_evidence,
        "supporting_evidence": supporting_evidence,
        "contradicting_evidence": contradicting_evidence,
        "strongest_evidence": (
            epistemic_evidence[0]
            if epistemic_evidence
            else None
        ),
        "gaps": gaps["identified_gaps"],
        "explanation": (
            "Estado atual calculado a partir das evidências atualmente "
            "vinculadas à IEC. Suporte e contradição são avaliados "
            "separadamente; a projeção não representa verdade científica absoluta."
        ),
    }


@app.get("/evidence")
def list_evidence(request: Request):
    """Lists persisted evidence after rebuilding the runtime EvidenceStore."""
    _hydrate_evidence_store_from_supabase(request)
    evidences = [e.to_dict() for e in evidence_store.evidences.values()]
    evidences.sort(key=lambda e: float(e.get("confidence") or 0), reverse=True)
    return {"evidence": evidences, "total": len(evidences), "stats": evidence_store.stats()}


# ==========================================================
# EVIDENCE VALIDATION
# ==========================================================

class IECRefIn(BaseModel):
    iec_id: str
    title: str
    statement: str
    knowledge_type: str
    confidence: float = 0.0


class IECCompareIn(BaseModel):
    iec_a: IECRefIn
    iec_b: IECRefIn


class IECRankIn(BaseModel):
    iecs: List[IECRefIn]


def _to_iec_contract(
    ref: IECRefIn,
) -> IECContract:
    return IECContract(
        iec_id=ref.iec_id,
        title=ref.title,
        statement=ref.statement,
        knowledge_type=ref.knowledge_type,
        confidence=ref.confidence,
    )


@app.post("/evidence-validation/iec")
def validate_iec_epistemic(
    payload: IECRefIn,
):
    return evidence_validator.validate_iec(
        _to_iec_contract(
            payload
        )
    )


@app.post("/evidence-validation/compare")
def compare_iec_support(
    payload: IECCompareIn,
):
    return evidence_validator.compare_iec_support(
        _to_iec_contract(
            payload.iec_a
        ),
        _to_iec_contract(
            payload.iec_b
        ),
    )


@app.post("/evidence-validation/diagnostic")
def generate_iec_diagnostic(
    payload: IECRefIn,
):
    return evidence_validator.generate_diagnostic(
        _to_iec_contract(
            payload
        )
    )


@app.post("/evidence-validation/gaps")
def analyze_iec_evidence_gaps(
    payload: IECRefIn,
):
    return evidence_validator.analyze_evidence_gaps(
        _to_iec_contract(
            payload
        )
    )


@app.post("/evidence-validation/rank")
def rank_iec_support(
    payload: IECRankIn,
):
    return evidence_validator.rank_iec_support(
        [
            _to_iec_contract(
                ref
            )
            for ref in payload.iecs
        ]
    )


@app.post("/evidence-validation/evidence/{evidence_id}")
def validate_evidence(
    evidence_id: str,
):
    evidence = evidence_store.get_evidence(
        evidence_id
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Evidência não encontrada: "
                f"{evidence_id}"
            ),
        )

    return evidence_validator.validate_evidence(
        evidence
    )


@app.get("/evidence-validation/history")
def get_evidence_validation_history():
    return evidence_validator.get_validation_history()


@app.get("/evidence-validation/stats")
def get_evidence_validation_stats():
    return evidence_validator.stats()


# ==========================================================
# PERSISTENT / PROJECT-SCOPED CMC
# ==========================================================

@app.post("/cmc/persistent/missions")
def persist_cmc_mission(payload: CmcMissionPersistIn, request: Request):
    try:
        result = supabase_client.create_cmc_mission(request.state.access_token, request.state.user["id"], payload.model_dump())
        return {"status":"created","mission":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/cmc/persistent/missions")
def list_persistent_cmc_missions(request: Request, project_id: Optional[str] = None, limit: int = 100):
    try: return {"missions": supabase_client.list_cmc_missions(request.state.access_token, project_id, limit)}
    except SupabaseError as exc: raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

# ==========================================================
# COMMAND & MISSION CENTER
# ==========================================================

class MissionCreateIn(BaseModel):
    name: str
    objective: str
    priority: str = "NORMAL"
    project_id: Optional[str] = None


class CommandIssueIn(BaseModel):
    mission_id: str
    name: str
    objective: str
    priority: str = "NORMAL"


class CommandExecuteIn(BaseModel):
    command_id: str
    executor: str


class DecisionRecordIn(BaseModel):
    mission_id: str
    action: str
    reason: str
    confidence: float = 0.0
    evidence: Optional[List[str]] = None
    alternatives: Optional[List[str]] = None


class ResourceRegisterIn(BaseModel):
    name: str
    total_capacity: float
    unit: str = "units"
    resource_type: str = "GENERIC"


class ResourceAllocateIn(BaseModel):
    mission_id: str
    resource_id: str
    amount: float


class ResourceReleaseIn(BaseModel):
    allocation_id: str


class RobotMissionDispatchIn(BaseModel):
    mission_id: str
    robot_id: str
    name: str
    objective: str
    priority: str = "NORMAL"


@app.post("/cmc/missions")
def create_mission(
    payload: MissionCreateIn,
    request: Request,
):
    mission = cmc.create_mission(
        payload.name,
        payload.objective,
        payload.priority,
        payload.project_id,
    )

    try:
        supabase_client.create_cmc_mission(request.state.access_token, request.state.user["id"], {"id": mission.mission_id, "project_id": mission.project_id, "name": mission.name, "objective": mission.objective, "priority": mission.priority, "status": getattr(mission.status, "value", str(mission.status)), "payload": {}})
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _dc(mission)


@app.get("/cmc/missions/{mission_id}")
def get_mission_overview(
    mission_id: str,
):
    return _guarded(
        cmc.mission_overview,
        mission_id,
    )


@app.post("/cmc/commands")
def issue_command(
    payload: CommandIssueIn,
    request: Request,
):
    command = _guarded(
        cmc.issue_command,
        payload.mission_id,
        payload.name,
        payload.objective,
        payload.priority,
    )

    try:
        supabase_client.persist_cmc_command(request.state.access_token, request.state.user["id"], command)
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _dc(command)


@app.post("/cmc/commands/execute")
def execute_command(
    payload: CommandExecuteIn,
    request: Request,
):
    result = _guarded(
        cmc.execute_command,
        payload.command_id,
        payload.executor,
    )

    try:
        command = cmc.command_center.get_command(payload.command_id)
        supabase_client._request("PATCH", "/rest/v1/cmc_commands", access_token=request.state.access_token, json={"status": getattr(command.status, "value", str(command.status)), "executor": payload.executor, "result": _dc(result)}, params={"id": f"eq.{payload.command_id}"}, prefer="return=representation")
    except Exception:
        pass
    return _dc(result)


@app.post("/cmc/decisions")
def record_decision(
    payload: DecisionRecordIn,
    request: Request,
):
    decision = _guarded(
        cmc.record_decision,
        payload.mission_id,
        payload.action,
        payload.reason,
        payload.confidence,
        payload.evidence,
        payload.alternatives,
    )

    try:
        supabase_client.persist_cmc_decision(request.state.access_token, request.state.user["id"], decision)
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _dc(decision)


@app.post("/cmc/resources")
def register_resource(
    payload: ResourceRegisterIn,
):
    resource = (
        cmc.resource_allocator.register_resource(
            name=payload.name,
            total_capacity=payload.total_capacity,
            unit=payload.unit,
            resource_type=payload.resource_type,
        )
    )

    return _dc(
        resource
    )


@app.post("/cmc/resources/allocate")
def allocate_resource(
    payload: ResourceAllocateIn,
    request: Request,
):
    allocation = _guarded(
        cmc.allocate_resource,
        payload.mission_id,
        payload.resource_id,
        payload.amount,
    )

    try:
        supabase_client.persist_cmc_resource(request.state.access_token, request.state.user["id"], allocation)
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _dc(allocation)


@app.post("/cmc/resources/release")
def release_resource(
    payload: ResourceReleaseIn,
):
    allocation = _guarded(
        cmc.release_resource,
        payload.allocation_id,
    )

    return _dc(
        allocation
    )


@app.get("/cmc/robots")
def list_cmc_robots():
    return _guarded(
        cmc.list_robots
    )


@app.post("/cmc/robots/dispatch")
def dispatch_mission_to_robot(
    payload: RobotMissionDispatchIn,
):
    return _guarded(
        cmc.send_mission_to_robot,
        payload.mission_id,
        payload.robot_id,
        payload.name,
        payload.objective,
        payload.priority,
    )


@app.get("/cmc/stats")
def get_cmc_stats():
    return cmc.stats()


@app.get("/cmc/health")
def get_cmc_health():
    return cmc.health_check()



# ==========================================================
# CMC LIFECYCLE PERSISTENCE
# ==========================================================

class MissionEvolutionIn(BaseModel):
    run_cognitive_cycle: bool = True


@app.post("/cmc/missions/{mission_id}/evolve")
def evolve_cmc_mission(mission_id: str, payload: MissionEvolutionIn, request: Request):
    """Formal CMC -> Cognitive Cycle -> Planner -> Local Agent proposal bridge."""
    try:
        rows = supabase_client.list_cmc_missions(request.state.access_token, limit=500)
        mission = next((item for item in (rows or []) if item.get("id") == mission_id), None)
        if not mission:
            raise HTTPException(status_code=404, detail="Persistent mission not found")
        if not mission.get("project_id"):
            raise HTTPException(status_code=409, detail="Mission must be associated with a project before creating an agent task")

        cognitive_result = None
        if payload.run_cognitive_cycle:
            cognitive_result = cognitive_orchestrator.run_cycle(
                statement=mission["objective"],
                submitted_by=request.state.user["id"],
                submission_type="cmc_mission",
            )
            iec = cognitive_result.get("iec") if isinstance(cognitive_result, dict) else None
            if iec is not None:
                supabase_client.persist_iec(request.state.access_token, request.state.user["id"], iec)
                _persist_graph_to_neo4j(iec, cognitive_result.get("connections", []))

        proposal = GovernedEvolutionCycle().propose(mission)
        plan = proposal["plan"]
        result = supabase_client.persist_agent_task(
            request.state.access_token, request.state.user["id"], mission["project_id"],
            f"Coding Agent — {mission['name']}", mission["objective"],
            80 if str(mission.get("priority", "NORMAL")).upper() in {"HIGH", "CRITICAL"} else 60,
            "coding_plan", plan["execution_spec"], mission_id=mission_id, plan=plan,
        )
        event = {"event_type": "agent_plan_proposed", "at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "plan_id": plan["plan_id"], "task_id": (result[0] if isinstance(result, list) and result else result).get("id") if isinstance((result[0] if isinstance(result, list) and result else result), dict) else None}
        supabase_client.append_cmc_mission_timeline(request.state.access_token, mission_id, event)
        supabase_client.persist_cmc_artifact("cmc_events", request.state.access_token, request.state.user["id"], {"mission_id": mission_id, "event_type": "agent_plan_proposed", "payload": event})
        return {"status": "planning", "mission": mission, "cognitive_cycle": _serialize_cycle_result(cognitive_result) if cognitive_result else None, "proposal": proposal, "task": result[0] if isinstance(result, list) and result else result}
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Mission evolution failed: {exc}") from exc


class MissionTransitionIn(BaseModel):
    state: str
    reason: Optional[str] = None


@app.post("/cmc/missions/{mission_id}/transition")
def transition_mission(mission_id: str, payload: MissionTransitionIn, request: Request):
    """Apply a validated runtime transition and persist both state and timeline event."""
    from core.mission.mission_state import MissionState
    try:
        next_state = MissionState(payload.state.upper())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid mission state") from exc
    try:
        from core.mission.mission import Mission
        persisted = supabase_client.list_cmc_missions(request.state.access_token, limit=500)
        row = next((item for item in (persisted or []) if item.get("id") == mission_id), None)
        if not row:
            raise HTTPException(status_code=404, detail="Persistent mission not found")
        try:
            mission = cmc._get_mission(mission_id)
        except (KeyError, ValueError, RuntimeError):
            mission = Mission(row["name"], row["objective"], row.get("priority", "NORMAL"), mission_id=mission_id, project_id=row.get("project_id"))
            mission.status = MissionState(str(row.get("status", "CREATED")).upper())
            mission.timeline = row.get("timeline") or mission.timeline
            cmc.mission_manager.registry.register(mission)
        previous = mission.status.value
        mission.change_state(next_state)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        values = {"status": next_state.value, "updated_at": now}
        supabase_client._request("PATCH", "/rest/v1/cmc_missions", access_token=request.state.access_token,
            json=values, params={"id": f"eq.{mission_id}"}, prefer="return=representation")
        event = {"event_type":"mission_state_changed", "at":now, "from":previous, "to":next_state.value, "reason":payload.reason}
        supabase_client.append_cmc_mission_timeline(request.state.access_token, mission_id, event)
        supabase_client.persist_cmc_artifact("cmc_events", request.state.access_token, request.state.user["id"], {
            "mission_id": mission_id,
            "event_type": "mission_state_changed",
            "payload": {"from": previous, "to": next_state.value, "reason": payload.reason},
        })
        return _dc(mission)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


# ==========================================================
# LOCAL AGENT SANDBOX EXECUTION
# ==========================================================

class AgentSandboxExecuteIn(BaseModel):
    task_id: str
    spec: Dict[str, Any] = Field(default_factory=dict)


@app.post("/agent/runtime/tasks/{task_id}/execute")
def agent_runtime_execute(task_id: str, payload: AgentSandboxExecuteIn, request: Request):
    """Execute an approved task using only explicit sandbox operations."""
    if payload.task_id != task_id:
        raise HTTPException(status_code=400, detail="task_id does not match path")
    try:
        tasks = supabase_client.list_agent_tasks(request.state.access_token, limit=500)
        task = next((item for item in (tasks or []) if item.get("id") == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.get("status") != "running":
            raise HTTPException(status_code=409, detail="Task must be running before execution")
        stored_spec = task.get("execution_spec") or {}
        if payload.spec and payload.spec != stored_spec:
            raise HTTPException(status_code=409, detail="Execution spec must match the approved task spec")
        spec = stored_spec
        if not spec:
            raise HTTPException(status_code=400, detail="Task has no approved execution spec")
        result = execute_task_spec(spec)
        status = "completed" if result.get("ok") else "failed"
        values = {"status": status, "result": {"sandbox": result}, "completed_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
        updated = supabase_client.update_agent_task(request.state.access_token, task_id, values)
        return {"status": status, "task": updated[0] if isinstance(updated, list) and updated else updated, "result": result}
    except LocalAgentSandboxError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=408, detail="Sandbox execution timed out") from exc
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

# ==========================================================
# EVENT BUS
# ==========================================================

class EventPublishIn(BaseModel):
    event_type: str
    source_id: str

    payload: Dict[str, Any] = Field(
        default_factory=dict
    )

    priority: str = "NORMAL"

    metadata: Dict[str, Any] = Field(
        default_factory=dict
    )


@app.post("/events/publish")
def publish_event(
    payload: EventPublishIn,
):
    try:
        event_type = EventType(
            payload.event_type
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "event_type inválido: "
                f"{payload.event_type}"
            ),
        ) from exc

    try:
        priority = EventPriority[
            payload.priority.upper()
        ]

    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "priority inválida: "
                f"{payload.priority}"
            ),
        ) from exc

    event = Event(
        event_type=event_type,
        source_id=payload.source_id,
        payload=payload.payload,
        priority=priority,
        metadata=payload.metadata,
    )

    event_bus.publish(
        event
    )

    return {
        "published": event.to_dict(),
        "subscriber_count": (
            event_bus.subscriber_count(
                event_type
            )
        ),
    }


@app.get("/events/types")
def list_event_types():
    return [
        event_type.value
        for event_type in EventType
    ]


@app.get("/events/subscribers/{event_type}")
def get_event_subscribers(
    event_type: str,
):
    try:
        event_type_enum = EventType(
            event_type
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                "event_type desconhecido: "
                f"{event_type}"
            ),
        ) from exc

    return {
        "event_type": event_type_enum.value,
        "subscriber_count": (
            event_bus.subscriber_count(
                event_type_enum
            )
        ),
        "has_subscribers": (
            event_bus.has_subscribers(
                event_type_enum
            )
        ),
    }


# ==========================================================
# SECURITY MANAGER
# ==========================================================

class ModulePermissionIn(BaseModel):
    permission: str


@app.post("/security/modules/{module_name}/trust")
def trust_module(
    module_name: str,
):
    security_manager.register_module(
        module_name
    )

    return {
        "module": module_name,
        "trusted": True,
    }


@app.delete("/security/modules/{module_name}/trust")
def untrust_module(
    module_name: str,
):
    security_manager.unregister_module(
        module_name
    )

    return {
        "module": module_name,
        "trusted": False,
    }


@app.get("/security/modules/{module_name}/trusted")
def is_module_trusted(
    module_name: str,
):
    return {
        "module": module_name,
        "trusted": (
            security_manager.is_trusted(
                module_name
            )
        ),
    }


@app.post("/security/modules/{module_name}/permissions")
def grant_module_permission(
    module_name: str,
    payload: ModulePermissionIn,
):
    security_manager.grant_permission(
        module_name,
        payload.permission,
    )

    return {
        "module": module_name,
        "permissions": (
            security_manager.list_permissions(
                module_name
            )
        ),
    }


@app.delete(
    "/security/modules/{module_name}/permissions/{permission}"
)
def revoke_module_permission(
    module_name: str,
    permission: str,
):
    security_manager.revoke_permission(
        module_name,
        permission,
    )

    return {
        "module": module_name,
        "permissions": (
            security_manager.list_permissions(
                module_name
            )
        ),
    }


@app.get("/security/modules/{module_name}/permissions")
def list_module_permissions(
    module_name: str,
):
    return {
        "module": module_name,
        "permissions": (
            security_manager.list_permissions(
                module_name
            )
        ),
    }
# ==========================================================
# WORKSPACE GOVERNANCE / PROJECT TEMPLATES / DURABLE CMC
# ==========================================================

class ProjectInvitationIn(BaseModel):
    project_id: str
    email: str
    role: str = "viewer"

class ProjectFromTemplateIn(BaseModel):
    template_slug: str
    slug: str
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None

class CmcArtifactIn(BaseModel):
    mission_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)

@app.get("/workspace/profiles")
def workspace_profiles(request: Request):
    try:
        profiles = supabase_client.select("workspace_profiles", request.state.access_token, filters={"order":"email.asc","limit":"500"})
        return {"profiles": profiles}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/workspace/projects/{project_id}/members")
def workspace_project_members(project_id: str, request: Request):
    try:
        memberships = supabase_client.list_project_memberships(request.state.access_token, project_id)
        ids = [m.get("user_id") for m in memberships if m.get("user_id")]
        profiles = []
        if ids:
            profiles = supabase_client.select("workspace_profiles", request.state.access_token, filters={"id": "in.(" + ",".join(ids) + ")", "limit":"500"})
        by_id = {p.get("id"): p for p in profiles}
        return {"members": [{**m, "profile": by_id.get(m.get("user_id"))} for m in memberships]}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

class ProjectMemberRoleIn(BaseModel):
    user_id: str
    role: str


@app.patch("/workspace/projects/{project_id}/members/{user_id}")
def workspace_update_member_role(project_id: str, user_id: str, payload: ProjectMemberRoleIn, request: Request):
    if payload.user_id != user_id:
        raise HTTPException(status_code=400, detail="user_id does not match path")
    if payload.role not in {"administrator","developer","researcher","operator","viewer"}:
        raise HTTPException(status_code=400, detail="Invalid project role")
    try:
        result = supabase_client.update_project_member_role(request.state.access_token, project_id, user_id, payload.role)
        return {"status": "updated", "membership": result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.delete("/workspace/projects/{project_id}/members/{user_id}")
def workspace_remove_member(project_id: str, user_id: str, request: Request):
    if user_id == request.state.user["id"]:
        raise HTTPException(status_code=400, detail="Use project ownership transfer before removing yourself")
    try:
        result = supabase_client.remove_project_member(request.state.access_token, project_id, user_id)
        return {"status": "removed", "membership": result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@app.get("/workspace/projects/{project_id}/invitations")
def workspace_project_invitations(project_id: str, request: Request):
    try:
        return {"invitations": supabase_client.list_project_invitations(request.state.access_token, project_id)}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/workspace/projects/{project_id}/invitations")
def workspace_create_invitation(project_id: str, payload: ProjectInvitationIn, request: Request):
    if payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_id does not match path")
    if payload.role not in {"administrator","developer","researcher","operator","viewer"}:
        raise HTTPException(status_code=400, detail="Invalid project role")
    try:
        result = supabase_client.create_project_invitation(request.state.access_token, request.state.user["id"], project_id, payload.email, payload.role)
        return {"status":"invited", "invitation": result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/workspace/projects/{project_id}/invitations/{invitation_id}/revoke")
def workspace_revoke_invitation(project_id: str, invitation_id: str, request: Request):
    try:
        result = supabase_client.revoke_project_invitation(request.state.access_token, invitation_id)
        return {"status":"revoked", "invitation": result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/projects/templates")
def project_templates(request: Request):
    try:
        return {"templates": supabase_client.list_project_templates(request.state.access_token)}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/projects/from-template")
def project_from_template(payload: ProjectFromTemplateIn, request: Request):
    try:
        templates = supabase_client.list_project_templates(request.state.access_token)
        template = next((t for t in templates if t.get("slug") == payload.template_slug), None)
        if not template:
            raise HTTPException(status_code=404, detail="Project template not found")
        config = template.get("configuration") or {}
        metadata = {"template_slug": template.get("slug"), "modules": config.get("modules", []), "engines": config.get("engines", []), "skills": config.get("skills", []), "cmc": bool(config.get("cmc", False)), "knowledge_graph": bool(config.get("knowledge_graph", False))}
        result = supabase_client.create_project(request.state.access_token, request.state.user["id"], {"slug":payload.slug.strip().lower().replace(" ","-"), "name":payload.name.strip(), "project_type":template.get("project_type") or "custom", "domain":payload.domain, "description":payload.description or template.get("description"), "status":"development", "metadata":metadata})
        return {"status":"created", "template":template, "project":result[0] if isinstance(result,list) and result else result}
    except HTTPException:
        raise
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

_CMC_TABLES = {"commands":"cmc_commands", "decisions":"cmc_decisions", "resources":"cmc_resource_allocations", "events":"cmc_events"}

@app.get("/cmc/persistent/missions/{mission_id}/artifacts")
def cmc_mission_artifacts(mission_id: str, request: Request):
    try:
        return {key: supabase_client.list_cmc_artifacts(table, request.state.access_token, mission_id) for key, table in _CMC_TABLES.items()}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/cmc/persistent/{artifact_type}")
def cmc_persist_artifact(artifact_type: str, payload: CmcArtifactIn, request: Request):
    table = _CMC_TABLES.get(artifact_type)
    if not table:
        raise HTTPException(status_code=404, detail="Unknown CMC artifact type")
    row = {"mission_id": payload.mission_id, **payload.payload}
    try:
        result = supabase_client.persist_cmc_artifact(table, request.state.access_token, request.state.user["id"], row)
        return {"status":"created", "artifact":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.get("/agent/instances")
def local_agent_instances(request: Request):
    try:
        return {"instances": supabase_client.list_agent_instances(request.state.access_token)}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

# ==========================================================
# LOCAL AGENT RUNTIME CONNECTOR
# ==========================================================

class AgentHeartbeatIn(BaseModel):
    instance_name: str = "local-dev"
    capabilities: List[str] = Field(default_factory=list)

class AgentClaimIn(BaseModel):
    instance_name: str = "local-dev"

class AgentCompleteIn(BaseModel):
    status: str = "completed"
    result: Dict[str, Any] = Field(default_factory=dict)

@app.post("/agent/runtime/heartbeat")
def agent_runtime_heartbeat(payload: AgentHeartbeatIn, request: Request):
    # Runtime identity is a normal authenticated workspace user. RLS remains the boundary.
    try:
        instance = supabase_client.upsert_agent_instance(request.state.access_token, request.state.user["id"], payload.instance_name, payload.capabilities)
        return {"status":"online", "instance_name":payload.instance_name, "user_id":request.state.user["id"], "capabilities":payload.capabilities, "instance": instance[0] if isinstance(instance,list) and instance else instance}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/agent/runtime/claim")
def agent_runtime_claim(payload: AgentClaimIn, request: Request):
    try:
        task = supabase_client.claim_next_agent_task(request.state.access_token, payload.instance_name)
        if not task or task == {} or task == "null":
            return {"status":"idle", "task":None}
        return {"status":"claimed", "task":task}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

@app.post("/agent/runtime/tasks/{task_id}/complete")
def agent_runtime_complete(task_id: str, payload: AgentCompleteIn, request: Request):
    if payload.status not in {"completed","failed","blocked"}:
        raise HTTPException(status_code=400, detail="Invalid completion status")
    try:
        values = {"status":payload.status, "result":payload.result, "completed_at":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
        result = supabase_client.update_agent_task(request.state.access_token, task_id, values)
        return {"status":payload.status, "task":result[0] if isinstance(result,list) and result else result}
    except SupabaseError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
