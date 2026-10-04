from persistence.session import Session
from persistence.transaction import Transaction
from persistence.unit_of_work import UnitOfWork
from persistence.repository_factory import (
    RepositoryFactory
)


class PersistenceManager:
    """
    Persistence Manager

    Orquestra a camada de persistência
    do KALATRACE.

    Responsável pelo ciclo de vida
    dos componentes de persistência.
    """

    def __init__(self):
        self.repository_factory = (
            RepositoryFactory()
        )

        self.initialized = False


    def initialize(self):
        """
        Inicializa a camada.
        """

        if self.initialized:
            return

        self.initialized = True


    def create_session(self):
        """
        Cria uma nova sessão.
        """

        if not self.initialized:
            raise RuntimeError(
                "PersistenceManager não inicializado."
            )

        return Session()


    def create_unit_of_work(self):
        """
        Cria uma unidade de trabalho.
        """

        session = self.create_session()

        transaction = Transaction()

        unit_of_work = UnitOfWork(
            session,
            transaction
        )

        return unit_of_work


    def get_repository(
        self,
        name: str
    ):
        """
        Recupera um repository.
        """

        return self.repository_factory.create(
            name
        )


    def shutdown(self):
        """
        Finaliza persistência.
        """

        self.repository_factory.clear()

        self.initialized = False