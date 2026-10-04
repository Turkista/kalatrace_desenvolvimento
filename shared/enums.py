"""
KALATRACE
Shared Enumerations

Camada:
Foundation Layer

Responsabilidade:
Centralizar os vocabulários controlados utilizados
por todos os módulos do sistema.

Blueprint:
Documento 71
"""

from enum import Enum


# ==========================================================
# Base Enum
# ==========================================================

class StrEnum(str, Enum):
    """
    Enumeração base do KALATRACE.

    Permite:
    - comportamento de Enum
    - comparação como string
    - serialização simples para APIs
    """

    def __str__(self):
        return self.value


# ==========================================================
# Knowledge Domain
# ==========================================================


class KnowledgeState(StrEnum):
    """
    Estado evolutivo de uma unidade de conhecimento.
    """

    CREATED = "created"
    DRAFT = "draft"
    HYPOTHESIS = "hypothesis"
    UNDER_REVIEW = "under_review"
    UNDER_VALIDATION = "under_validation"
    VALIDATED = "validated"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    ARCHIVED = "archived"



class EvidenceType(StrEnum):
    """
    Tipos de evidências científicas aceitas.
    """

    CLINICAL_TRIAL = "clinical_trial"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OBSERVATIONAL_STUDY = "observational_study"
    CASE_REPORT = "case_report"
    EXPERIMENTAL_STUDY = "experimental_study"
    ANIMAL_STUDY = "animal_study"
    IN_VITRO = "in_vitro"
    REVIEW_ARTICLE = "review_article"
    EXPERT_OPINION = "expert_opinion"



class EvidenceLevel(StrEnum):
    """
    Força hierárquica da evidência.
    """

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"



class ConfidenceLevel(StrEnum):
    """
    Grau de confiança calculado pelo sistema.
    """

    UNKNOWN = "unknown"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
# ==========================================================
# Identity Domain
# ==========================================================


class IdentifierType(StrEnum):
    """
    Tipos de identificadores utilizados pelo KALATRACE.
    """

    KNOWLEDGE = "knowledge"

    IEC = "iec"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    CONCEPT = "concept"
    QUESTION = "question"
    DISCOVERY = "discovery"
    INSIGHT = "insight"
    AGENT = "agent"
    ENGINE = "engine"
    EVENT = "event"



class EntityType(StrEnum):
    """
    Tipos de entidades existentes no ecossistema KALATRACE.
    """

    KNOWLEDGE = "knowledge"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    DISCOVERY = "discovery"
    INSIGHT = "insight"
    SOURCE = "source"
    DOCUMENT = "document"
    AGENT = "agent"



# ==========================================================
# Graph Domain
# ==========================================================


class NodeType(StrEnum):
    """
    Tipos de nós possíveis no grafo de conhecimento.
    """

    IEC = "iec"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    CONCEPT = "concept"
    DISCOVERY = "discovery"
    QUESTION = "question"
    INSIGHT = "insight"
    DOCUMENT = "document"
    AUTHOR = "author"
    ORGANIZATION = "organization"



class EdgeType(StrEnum):
    """
    Tipos de relações entre nós do grafo.
    """

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    EXTENDS = "extends"
    REFINES = "refines"
    ANSWERS = "answers"
    GENERATED_BY = "generated_by"
    VALIDATED_BY = "validated_by"
    REPLACED_BY = "replaced_by"



class RelationshipType(StrEnum):
    """
    Relações semânticas utilizadas na ontologia.
    """

    IS_A = "is_a"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"
    ASSOCIATED_WITH = "associated_with"
    CAUSES = "causes"
    INFLUENCES = "influences"
    ACTIVATES = "activates"
    INHIBITS = "inhibits"
    TREATS = "treats"
    PREVENTS = "prevents"
    CORRELATED_WITH = "correlated_with"
# ==========================================================
# Engine Domain
# ==========================================================


class EngineStatus(StrEnum):
    """
    Estados possíveis de execução de qualquer Engine.
    """

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"



class EngineType(StrEnum):
    """
    Engines cognitivas e científicas do KALATRACE.
    """

    COGNITIVE_ORCHESTRATOR = "cognitive_orchestrator"
    SCIENTIFIC_RESEARCH = "scientific_research"
    SCIENTIFIC_CONTEXT = "scientific_context"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"
    REASONING = "reasoning"
    CURIOSITY = "curiosity"
    RESEARCH_STRATEGY = "research_strategy"
    VALIDATION = "validation"
    INFERENCE = "inference"



# ==========================================================
# Agent Domain
# ==========================================================


class AgentType(StrEnum):
    """
    Tipos de agentes especializados.
    """

    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    REASONING = "reasoning"
    CURIOSITY = "curiosity"
    VALIDATION = "validation"
    DISCOVERY = "discovery"
    KNOWLEDGE_CURATOR = "knowledge_curator"



class AgentStatus(StrEnum):
    """
    Estado operacional dos agentes.
    """

    CREATED = "created"
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    OFFLINE = "offline"



# ==========================================================
# Orchestration Domain
# ==========================================================


class WorkflowStatus(StrEnum):
    """
    Estados de execução de workflows.
    """

    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"



class TaskStatus(StrEnum):
    """
    Estados de tarefas internas.
    """

    PENDING = "pending"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"



class ExecutionMode(StrEnum):
    """
    Modos de execução do sistema.
    """

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    AUTONOMOUS = "autonomous"
    HUMAN_ASSISTED = "human_assisted"
# ==========================================================
# Scientific Research Domain
# ==========================================================


class ResearchStatus(StrEnum):
    """
    Estados do ciclo de uma investigação científica.
    """

    CREATED = "created"
    PLANNING = "planning"
    SEARCHING = "searching"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"



class ResearchType(StrEnum):
    """
    Tipos de investigação realizados pelo KALATRACE.
    """

    LITERATURE_REVIEW = "literature_review"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    HYPOTHESIS_INVESTIGATION = "hypothesis_investigation"
    KNOWLEDGE_EXPLORATION = "knowledge_exploration"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    DISCOVERY_RESEARCH = "discovery_research"



class SourceType(StrEnum):
    """
    Tipos de fontes científicas externas.
    """

    PUBMED = "pubmed"
    CROSSREF = "crossref"
    SCOPUS = "scopus"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    JOURNAL = "journal"
    CONFERENCE = "conference"
    BOOK = "book"
    DATABASE = "database"



# ==========================================================
# Acquisition Domain
# ==========================================================


class DocumentType(StrEnum):
    """
    Tipos de documentos processados pelo sistema.
    """

    PDF = "pdf"
    HTML = "html"
    XML = "xml"
    JSON = "json"
    TEXT = "text"



class ParserType(StrEnum):
    """
    Tipos de processadores de documentos.
    """

    PDF_PARSER = "pdf_parser"
    HTML_PARSER = "html_parser"
    XML_PARSER = "xml_parser"
    TEXT_PARSER = "text_parser"
    SEMANTIC_PARSER = "semantic_parser"



class AcquisitionStatus(StrEnum):
    """
    Estado da aquisição de informação.
    """

    INITIALIZED = "initialized"
    CONNECTING = "connecting"
    RETRIEVING = "retrieving"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"



# ==========================================================
# Curation Domain
# ==========================================================


class CurationStatus(StrEnum):
    """
    Estados do processo de curadoria científica.
    """

    RECEIVED = "received"
    SCREENING = "screening"
    NORMALIZING = "normalizing"
    DEDUPLICATING = "deduplicating"
    CURATED = "curated"
    REJECTED = "rejected"



class DataQualityLevel(StrEnum):
    """
    Qualidade dos dados processados.
    """

    UNKNOWN = "unknown"
    POOR = "poor"
    ACCEPTABLE = "acceptable"
    GOOD = "good"
    EXCELLENT = "excellent"
# ==========================================================
# Validation Domain
# ==========================================================


class ValidationStatus(StrEnum):
    """
    Estados do ciclo de validação.
    """

    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"



class ValidationType(StrEnum):
    """
    Tipos de validação executados pelo sistema.
    """

    EVIDENCE_VALIDATION = "evidence_validation"
    GRAPH_VALIDATION = "graph_validation"
    CONSISTENCY_VALIDATION = "consistency_validation"
    ONTOLOGY_VALIDATION = "ontology_validation"
    LOGICAL_VALIDATION = "logical_validation"
    SOURCE_VALIDATION = "source_validation"



# ==========================================================
# Inference Domain
# ==========================================================


class InferenceType(StrEnum):
    """
    Tipos de inferência utilizados pelo KALATRACE.
    """

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    PROBABILISTIC = "probabilistic"
    SYMBOLIC = "symbolic"
    HYBRID = "hybrid"



class InferenceStatus(StrEnum):
    """
    Estado de uma operação de inferência.
    """

    CREATED = "created"
    EXECUTING = "executing"
    GENERATED = "generated"
    VERIFIED = "verified"
    REJECTED = "rejected"



# ==========================================================
# Reasoning Domain
# ==========================================================


class ReasoningMode(StrEnum):
    """
    Modos de raciocínio utilizados pelos agentes e engines.
    """

    LOGICAL = "logical"
    SCIENTIFIC = "scientific"
    CAUSAL = "causal"
    ANALOGICAL = "analogical"
    PROBABILISTIC = "probabilistic"
    EXPLORATORY = "exploratory"



class ReasoningStatus(StrEnum):
    """
    Estados de um processo de raciocínio.
    """

    STARTED = "started"
    ANALYZING = "analyzing"
    EXPLAINING = "explaining"
    COMPLETED = "completed"
    FAILED = "failed"



# ==========================================================
# Knowledge Evolution Domain
# ==========================================================


class EvolutionType(StrEnum):
    """
    Formas de evolução do conhecimento.
    """

    CREATION = "creation"
    UPDATE = "update"
    REFINEMENT = "refinement"
    MERGE = "merge"
    CONFLICT_RESOLUTION = "conflict_resolution"
    REPLACEMENT = "replacement"



class EvolutionStatus(StrEnum):
    """
    Estados do processo evolutivo.
    """

    DETECTED = "detected"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
# ==========================================================
# Governance Domain
# ==========================================================


class GovernanceLevel(StrEnum):
    """
    Níveis de governança aplicados ao conhecimento.
    """

    NONE = "none"
    BASIC = "basic"
    CONTROLLED = "controlled"
    STRICT = "strict"
    CRITICAL = "critical"



class AuditStatus(StrEnum):
    """
    Estado dos registros de auditoria.
    """

    CREATED = "created"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    RESOLVED = "resolved"



class AuditAction(StrEnum):
    """
    Tipos de ações auditáveis.
    """

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    VALIDATE = "validate"
    APPROVE = "approve"
    REJECT = "reject"



# ==========================================================
# Provenance Domain
# ==========================================================


class ProvenanceType(StrEnum):
    """
    Origem de uma informação ou conhecimento.
    """

    HUMAN = "human"
    AGENT = "agent"
    ENGINE = "engine"
    DATABASE = "database"
    LITERATURE = "literature"
    SIMULATION = "simulation"
    INFERENCE = "inference"



class ProvenanceSource(StrEnum):
    """
    Fontes de origem rastreáveis.
    """

    SCIENTIFIC_PUBLICATION = "scientific_publication"
    CLINICAL_DATA = "clinical_data"
    EXPERIMENTAL_DATA = "experimental_data"
    GENERATED_KNOWLEDGE = "generated_knowledge"
    USER_INPUT = "user_input"



# ==========================================================
# Version Domain
# ==========================================================


class VersionStatus(StrEnum):
    """
    Estado de uma versão de conhecimento.
    """

    INITIAL = "initial"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"



class ChangeType(StrEnum):
    """
    Tipo de alteração realizada em uma entidade.
    """

    CREATION = "creation"
    MODIFICATION = "modification"
    MERGE = "merge"
    SPLIT = "split"
    RESTORATION = "restoration"



# ==========================================================
# Event System Domain
# ==========================================================


class EventType(StrEnum):
    """
    Eventos internos do sistema.
    """

    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"

    KNOWLEDGE_CREATED = "knowledge_created"
    KNOWLEDGE_UPDATED = "knowledge_updated"

    EVIDENCE_ADDED = "evidence_added"
    HYPOTHESIS_CREATED = "hypothesis_created"

    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"

    GRAPH_UPDATED = "graph_updated"

    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"

    ENGINE_STARTED = "engine_started"
    ENGINE_COMPLETED = "engine_completed"
# ==========================================================
# Curiosity Domain
# ==========================================================


class CuriosityType(StrEnum):
    """
    Tipos de curiosidade computacional do KALATRACE.
    """

    KNOWLEDGE_GAP = "knowledge_gap"
    CONTRADICTION = "contradiction"
    NOVELTY = "novelty"
    OPPORTUNITY = "opportunity"
    UNCERTAINTY = "uncertainty"
    CONNECTION = "connection"



class CuriosityStatus(StrEnum):
    """
    Estados de uma iniciativa de curiosidade.
    """

    GENERATED = "generated"
    ANALYZING = "analyzing"
    PRIORITIZED = "prioritized"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISCARDED = "discarded"



# ==========================================================
# Discovery Domain
# ==========================================================


class DiscoveryType(StrEnum):
    """
    Tipos de descobertas realizadas pelo sistema.
    """

    NEW_RELATIONSHIP = "new_relationship"
    NEW_HYPOTHESIS = "new_hypothesis"
    KNOWLEDGE_GAP = "knowledge_gap"
    PATTERN = "pattern"
    CONTRADICTION = "contradiction"
    EMERGING_CONCEPT = "emerging_concept"



class DiscoveryStatus(StrEnum):
    """
    Estados de uma descoberta.
    """

    DETECTED = "detected"
    EXPLORING = "exploring"
    ANALYZING = "analyzing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    INCORPORATED = "incorporated"



# ==========================================================
# Research Strategy Domain
# ==========================================================


class StrategyType(StrEnum):
    """
    Estratégias de investigação científica.
    """

    EXPLORATION = "exploration"
    VALIDATION = "validation"
    COMPARISON = "comparison"
    REPLICATION = "replication"
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    GAP_ANALYSIS = "gap_analysis"



class PriorityLevel(StrEnum):
    """
    Prioridade atribuída pelo sistema.
    """

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"



# ==========================================================
# Metacognition Domain
# ==========================================================


class ReflectionType(StrEnum):
    """
    Tipos de reflexão interna do sistema.
    """

    PERFORMANCE = "performance"
    KNOWLEDGE_QUALITY = "knowledge_quality"
    DECISION_ANALYSIS = "decision_analysis"
    ERROR_ANALYSIS = "error_analysis"
    STRATEGY_REVIEW = "strategy_review"



class SelfAssessmentStatus(StrEnum):
    """
    Estado de autoavaliação.
    """

    INITIATED = "initiated"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    REQUIRES_ADJUSTMENT = "requires_adjustment"
# ==========================================================
# Persistence Domain
# ==========================================================


class StorageType(StrEnum):
    """
    Tipos de armazenamento utilizados pelo KALATRACE.
    """

    MEMORY = "memory"
    FILESYSTEM = "filesystem"
    POSTGRES = "postgres"
    NEO4J = "neo4j"
    ELASTICSEARCH = "elasticsearch"
    CACHE = "cache"



class RepositoryStatus(StrEnum):
    """
    Estado de um repositório persistente.
    """

    CREATED = "created"
    CONNECTED = "connected"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"



class TransactionStatus(StrEnum):
    """
    Estados de transações persistentes.
    """

    STARTED = "started"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"



# ==========================================================
# Configuration Domain
# ==========================================================


class EnvironmentType(StrEnum):
    """
    Ambientes de execução.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"



class LogLevel(StrEnum):
    """
    Níveis de registro do sistema.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"



# ==========================================================
# Security Domain
# ==========================================================


class AccessLevel(StrEnum):
    """
    Níveis de acesso aos recursos.
    """

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"



class AuthenticationType(StrEnum):
    """
    Métodos de autenticação.
    """

    NONE = "none"
    TOKEN = "token"
    API_KEY = "api_key"
    SERVICE_ACCOUNT = "service_account"



# ==========================================================
# API Domain
# ==========================================================


class RequestStatus(StrEnum):
    """
    Estados de requisições da API.
    """

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"



class ResponseType(StrEnum):
    """
    Tipos de resposta da API.
    """

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"



# ==========================================================
# System Domain
# ==========================================================


class SystemStatus(StrEnum):
    """
    Estado geral do KALATRACE.
    """

    INITIALIZING = "initializing"
    ONLINE = "online"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"



class HealthStatus(StrEnum):
    """
    Saúde dos componentes internos.
    """

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"