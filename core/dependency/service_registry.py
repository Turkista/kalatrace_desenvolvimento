"""
KALATRACE Service Registry

Migrated from kernel/dependency/service_registry.py
as part of ADR-001 (T1.1b) — no prior equivalent in core/.
"""

from typing import Dict, Any


class ServiceRegistry:
    """
    KALATRACE Service Registry

    Responsável pelo registro, descoberta
    e gerenciamento do ciclo de vida dos
    serviços disponíveis no Kernel.
    """

    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.initialized = False


    def initialize(self):
        """
        Inicializa o registro de serviços.
        """

        if self.initialized:
            return

        self.initialized = True


    def register(
        self,
        name: str,
        service: Any
    ):
        """
        Registra um serviço no Kernel.

        Args:
            name:
                Identificador único do serviço.

            service:
                Instância do serviço.
        """

        self._ensure_initialized()

        if not name:
            raise ValueError(
                "Service name cannot be empty."
            )

        if service is None:
            raise ValueError(
                "Service instance cannot be None."
            )

        self.services[name] = service


    def get(
        self,
        name: str
    ):
        """
        Recupera um serviço registrado.
        """

        self._ensure_initialized()

        if name not in self.services:
            raise KeyError(
                f"Service not found: {name}"
            )

        return self.services[name]


    def exists(
        self,
        name: str
    ) -> bool:
        """
        Verifica se um serviço existe.
        """

        return name in self.services


    def remove(
        self,
        name: str
    ):
        """
        Remove um serviço registrado.
        """

        if name in self.services:
            del self.services[name]


    def list_services(self):
        """
        Lista serviços disponíveis.
        """

        return list(
            self.services.keys()
        )


    def shutdown(self):
        """
        Finaliza o registro de serviços.
        """

        self.services.clear()

        self.initialized = False


    def _ensure_initialized(self):
        """
        Garante que o registry esteja ativo.
        """

        if not self.initialized:
            raise RuntimeError(
                "Service Registry not initialized."
            )