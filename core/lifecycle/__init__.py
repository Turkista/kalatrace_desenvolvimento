"""
KALATRACE Core

Lifecycle package.

Public lifecycle API responsible for:

- Component state representation
- Lifecycle execution contracts
- Transition validation
- State machine governance

This package exposes the official lifecycle
interfaces and implementations used by
executable KALATRACE components.
"""


from .component_state import (
    ComponentState,
)


from .lifecycle_state_machine import (
    LifecycleStateMachine,
)


from .lifecycle import (
    Lifecycle,
)


from .kernel_module import (
    KernelModule,
)


from .lifecycle_manager import (
    LifecycleManager,
)



__all__ = [

    # State model
    "ComponentState",


    # State governance
    "LifecycleStateMachine",


    # Lifecycle implementation
    "Lifecycle",


    # Multi-module orchestration (migrated T1.1d)
    "KernelModule",
    "LifecycleManager",

]