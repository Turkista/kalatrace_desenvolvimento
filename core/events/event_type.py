"""
KALATRACE Core

Event Type

Defines standard event identifiers used
throughout the architecture.
"""

from enum import Enum


class EventType(str, Enum):
    """
    Standard event types used by KALATRACE.
    """


    # ---------------------------------
    # Component Lifecycle
    # ---------------------------------

    COMPONENT_REGISTERED = (
        "component_registered"
    )

    COMPONENT_UNREGISTERED = (
        "component_unregistered"
    )

    COMPONENT_LOADED = (
        "component_loaded"
    )

    COMPONENT_UNLOADED = (
        "component_unloaded"
    )

    COMPONENT_STARTED = (
        "component_started"
    )

    COMPONENT_STOPPED = (
        "component_stopped"
    )

    COMPONENT_FAILED = (
        "component_failed"
    )


    # ---------------------------------
    # Runtime Lifecycle
    # ---------------------------------

    RUNTIME_INITIALIZED = (
        "runtime_initialized"
    )

    RUNTIME_STARTED = (
        "runtime_started"
    )

    RUNTIME_STOPPED = (
        "runtime_stopped"
    )

    RUNTIME_FAILED = (
        "runtime_failed"
    )


    # ---------------------------------
    # Runtime Context
    # ---------------------------------

    RUNTIME_CONTEXT_CHANGED = (
        "runtime_context_changed"
    )

    CONFIGURATION_CHANGED = (
        "configuration_changed"
    )


    # ---------------------------------
    # Knowledge Lifecycle
    #
    # Reserved for:
    # - IEC
    # - Evidence
    # - Knowledge Graph
    # - Research Engines
    # ---------------------------------

    KNOWLEDGE_CREATED = (
        "knowledge_created"
    )

    KNOWLEDGE_UPDATED = (
        "knowledge_updated"
    )

    KNOWLEDGE_VALIDATED = (
        "knowledge_validated"
    )

    KNOWLEDGE_DEPRECATED = (
        "knowledge_deprecated"
    )

    EVIDENCE_REGISTERED = (
        "evidence_registered"
    )

    HYPOTHESIS_CREATED = (
        "hypothesis_created"
    )

    HYPOTHESIS_UPDATED = (
        "hypothesis_updated"
    )


    # ---------------------------------
    # Governance / Audit
    #
    # Reserved for:
    # - Traceability
    # - Scientific governance
    # - Decision history
    # ---------------------------------

    AUDIT_CREATED = (
        "audit_created"
    )

    AUDIT_UPDATED = (
        "audit_updated"
    )

    TRACE_STARTED = (
        "trace_started"
    )

    TRACE_COMPLETED = (
        "trace_completed"
    )


    # ---------------------------------
    # System / Infrastructure
    #
    # Reserved for:
    # - Kernel
    # - Diagnostics
    # - Monitoring
    # ---------------------------------

    SYSTEM_STARTED = (
        "system_started"
    )

    SYSTEM_STOPPED = (
        "system_stopped"
    )

    SYSTEM_WARNING = (
        "system_warning"
    )

    SYSTEM_ERROR = (
        "system_error"
    )

    HEALTH_CHECK_FAILED = (
        "health_check_failed"
    )

    DEPENDENCY_MISSING = (
        "dependency_missing"
    )


    # ---------------------------------
    # Extension
    # ---------------------------------

    CUSTOM = (
        "custom"
    )