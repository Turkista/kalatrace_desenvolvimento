"""
KALATRACE Kernel

Central system orchestrator.

Responsible for:
- dependency management;
- service registration;
- event system;
- module lifecycle.
"""


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

from core.events.event_bus import (
    EventBus
)

from core.lifecycle.lifecycle_manager import (
    LifecycleManager
)



class Kernel:
    """
    Main KALATRACE Kernel.

    Coordinates the internal infrastructure
    required by the system.
    """


    def __init__(
        self
    ):

        self.running = False


        # Dependency system

        self.dependency_container = (
            DependencyContainer()
        )


        self.service_registry = (
            ServiceRegistry()
        )


        self.injector = None



        # Communication

        self.event_bus = (
            EventBus()
        )


        # Module lifecycle

        self.lifecycle_manager = (
            LifecycleManager()
        )



    # =================================================
    # Boot
    # =================================================

    def initialize(
        self
    ):
        """
        Initializes Kernel infrastructure.
        """

        if self.running:
            return


        # Initialize dependency layer

        self.dependency_container.initialize()


        self.service_registry.initialize()


        # Connect service locator

        ServiceLocator.configure(
            self.service_registry
        )


        # Create injector

        self.injector = Injector(
            self.service_registry
        )


        # Initialize event system

        self.event_bus.initialize()



    def start(
        self
    ):
        """
        Starts Kernel execution.
        """

        if self.running:
            return


        self.lifecycle_manager.initialize_all()


        self.lifecycle_manager.start_all()


        self.running = True



    # =================================================
    # Shutdown
    # =================================================

    def stop(
        self
    ):
        """
        Stops Kernel execution.
        """

        if not self.running:
            return


        self.lifecycle_manager.stop_all()


        self.lifecycle_manager.shutdown_all()


        self.event_bus.shutdown()


        self.service_registry.shutdown()


        self.dependency_container.shutdown()


        ServiceLocator.clear()


        self.running = False



    # =================================================
    # Registration
    # =================================================

    def register_service(
        self,
        name,
        service
    ):
        """
        Registers a Kernel service.
        """

        self.service_registry.register(
            name,
            service
        )


        self.dependency_container.register(
            name,
            service
        )



    def register_module(
        self,
        module
    ):
        """
        Registers a Kernel module.
        """

        self.lifecycle_manager.register_module(
            module
        )



    # =================================================
    # Information
    # =================================================

    def status(
        self
    ):
        """
        Returns Kernel status.
        """

        return {
            "running": self.running,
            "services":
                self.service_registry.list_services(),
            "modules":
                self.lifecycle_manager.list_modules()
        }



    def __repr__(
        self
    ):

        return (
            f"<KALATRACE Kernel "
            f"running={self.running}>"
        )