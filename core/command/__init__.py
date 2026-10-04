"""
KALATRACE Command Center

Public command orchestration API.

This package exposes the official command
management interfaces used by KALATRACE.

Provides:

- Command entity
- Command lifecycle management
- Command execution routing
- Command results
- Command context
- Command history
- Command Center facade
"""


# =================================================
# Core Entity
# =================================================

from .command import Command



# =================================================
# Lifecycle
# =================================================

from .command_status import (
    CommandStatus,
    CommandStateMachine,
)



# =================================================
# Registry and Management
# =================================================

from .command_registry import CommandRegistry

from .command_manager import CommandManager



# =================================================
# Execution Pipeline
# =================================================

from .command_queue import CommandQueue

from .command_dispatcher import CommandDispatcher

from .command_executor import CommandExecutor



# =================================================
# Supporting Models
# =================================================

from .command_result import CommandResult

from .command_context import CommandContext

from .command_history import CommandHistory



# =================================================
# Service Layer
# =================================================

from .command_service import CommandService



# =================================================
# Command Center Facade
# =================================================

from .command_center import CommandCenter



__all__ = [

    # Core Entity

    "Command",


    # Lifecycle

    "CommandStatus",
    "CommandStateMachine",


    # Registry

    "CommandRegistry",


    # Management

    "CommandManager",


    # Execution

    "CommandQueue",
    "CommandDispatcher",
    "CommandExecutor",


    # Models

    "CommandResult",
    "CommandContext",
    "CommandHistory",


    # Service

    "CommandService",


    # Facade

    "CommandCenter",

]