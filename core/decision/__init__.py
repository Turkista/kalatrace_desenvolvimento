"""
KALATRACE Decision Controller

Public decision oversight API.

This package implements the "Decision Oversight" concept
from the Command & Mission Center specification: every
decision tracked here carries an action, a reason, a
confidence value, supporting evidence, and the alternatives
that were considered.

Provides:

- Decision entity
- Decision lifecycle management (PROPOSED / ACCEPTED /
  REJECTED / SUPERSEDED / ARCHIVED)
- Decision registry
- Decision Controller facade
"""

from __future__ import annotations


# =================================================
# Core Entity
# =================================================

from .decision import Decision


# =================================================
# Lifecycle
# =================================================

from .decision_status import (
    DecisionStatus,
    DecisionStateMachine,
)


# =================================================
# Registry
# =================================================

from .decision_registry import DecisionRegistry


# =================================================
# Facade
# =================================================

from .decision_controller import DecisionController


__all__ = [

    "Decision",

    "DecisionStatus",

    "DecisionStateMachine",

    "DecisionRegistry",

    "DecisionController",

]
