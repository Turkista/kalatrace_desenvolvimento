"""
KALATRACE Kernel Package

Public interface for the Kernel layer.
"""


from kernel.kernel import Kernel

from kernel.boot import KernelBoot

from core.events.event_bus import (
    EventBus
)

from core.events.event import (
    Event as KernelEvent
)

from core.lifecycle.lifecycle_manager import (
    LifecycleManager
)

from core.lifecycle.kernel_module import (
    KernelModule
)

from core.dependency.dependency_container import (
    DependencyContainer
)

from core.dependency.service_registry import (
    ServiceRegistry
)

from core.dependency.service_locator import (
    ServiceLocator
)

from core.dependency.injector import (
    Injector
)


__all__ = [

    # Core Kernel

    "Kernel",
    "KernelBoot",


    # Communication

    "EventBus",
    "KernelEvent",


    # Lifecycle

    "LifecycleManager",
    "KernelModule",


    # Dependency System

    "DependencyContainer",
    "ServiceRegistry",
    "ServiceLocator",
    "Injector",
]