"""
KALATRACE Core Contracts

Public contracts and interfaces used throughout
the KALATRACE architecture.
"""

from core.contracts.lifecycle_contract import (
    LifecycleContract,
)

from core.contracts.module_contract import (
    ModuleContract,
)

from core.contracts.engine_contract import (
    EngineContract,
)

from core.contracts.service_contract import (
    ServiceContract,
)

from core.contracts.command_contract import (
    CommandContract,
)

from core.contracts.mission_contract import (
    MissionContract,
    MissionStatus,
)

from core.contracts.repository_contract import (
    RepositoryContract,
)


__all__ = [

    # Base lifecycle
    "LifecycleContract",

    # Runtime modules
    "ModuleContract",
    "EngineContract",
    "ServiceContract",

    # Execution
    "CommandContract",
    "MissionContract",
    "MissionStatus",

    # Persistence
    "RepositoryContract",
]