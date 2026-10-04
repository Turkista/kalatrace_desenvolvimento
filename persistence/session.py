from typing import Optional

from persistence.persistence_context import (
    PersistenceContext
)


class Session:
    """
    Persistence Session

    Representa uma sessão ativa
    de persistência do KALATRACE.

    Gerencia o ciclo de vida do
    PersistenceContext.
    """

    def __init__(self):
        self.context: Optional[
            PersistenceContext
        ] = None

        self.active = False


    def open(self):
        """
        Abre uma nova sessão
        de persistência.
        """

        if self.active:
            raise RuntimeError(
                "Sessão já está ativa."
            )

        self.context = PersistenceContext()

        self.active = True


    def get_context(self):
        """
        Retorna o contexto atual.
        """

        if not self.active:
            raise RuntimeError(
                "Sessão não está ativa."
            )

        return self.context


    def close(self):
        """
        Fecha a sessão atual.
        """

        if not self.active:
            return

        self.context.clear()

        self.context = None

        self.active = False


    def is_active(self) -> bool:
        """
        Verifica se existe uma sessão ativa.
        """

        return self.active