"""
KALATRACE Lifecycle Manager

Coordinates the lifecycle of every orchestrated
module (start/stop/initialize/shutdown ordering).

Migrated from kernel/lifecycle/lifecycle_manager.py
as part of ADR-001 (T1.1d). Confirmed in T0.2/T1.1a:
this is a distinct responsibility from
core.lifecycle.Lifecycle/LifecycleStateMachine
(per-component state machine) — it coordinates
*multiple* modules, so it was added as a new
capability rather than merged into the existing
state-machine classes.
"""

from typing import Dict

from core.lifecycle.kernel_module import KernelModule



class LifecycleManager:
    """
    Coordinates lifecycle operations
    of Kernel modules.
    """


    def __init__(self):

        self.modules: Dict[
            str,
            KernelModule
        ] = {}

        self.initialized = False



    # =================================================
    # Registration
    # =================================================

    def register_module(
        self,
        module: KernelModule
    ):

        if module.name in self.modules:

            raise ValueError(
                f"Module already registered: "
                f"{module.name}"
            )


        self.modules[
            module.name
        ] = module



    def unregister_module(
        self,
        name: str
    ):

        self.modules.pop(
            name,
            None
        )



    # =================================================
    # Lifecycle
    # =================================================

    def initialize_all(
        self
    ):

        for module in self.modules.values():

            if not module.initialized:

                module.initialize()


        self.initialized = True



    def start_all(
        self
    ):

        if not self.initialized:

            raise RuntimeError(
                "Lifecycle Manager not initialized."
            )


        for module in self.modules.values():

            if (
                module.initialized
                and
                not module.running
            ):

                module.start()



    def stop_all(
        self
    ):

        for module in reversed(
            list(
                self.modules.values()
            )
        ):

            if module.running:

                module.stop()



    def shutdown_all(
        self
    ):

        for module in reversed(
            list(
                self.modules.values()
            )
        ):

            if module.initialized:

                module.shutdown()


        self.initialized = False



    # =================================================
    # Queries
    # =================================================

    def get_module(
        self,
        name: str
    ) -> KernelModule | None:

        return self.modules.get(
            name
        )



    def has_module(
        self,
        name: str
    ) -> bool:

        return name in self.modules



    def list_modules(
        self
    ) -> list[str]:

        return list(
            self.modules.keys()
        )



    def module_count(
        self
    ) -> int:

        return len(
            self.modules
        )



    def clear(
        self
    ):

        self.modules.clear()



    def __repr__(
        self
    ):

        return (
            f"<LifecycleManager "
            f"modules={len(self.modules)}>"
        )