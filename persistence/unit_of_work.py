from persistence.session import Session
from persistence.transaction import Transaction


class UnitOfWork:
    """
    Unit Of Work

    Coordena operações de persistência
    do KALATRACE.

    Agrupa alterações relacionadas
    em uma única operação.
    """

    def __init__(
        self,
        session: Session,
        transaction: Transaction
    ):
        self.session = session
        self.transaction = transaction

        self.repositories = {}

        self.active = False


    def register_repository(
        self,
        name: str,
        repository
    ):
        """
        Registra um repository
        disponível na unidade.
        """

        self.repositories[name] = repository


    def get_repository(
        self,
        name: str
    ):
        """
        Recupera um repository.
        """

        if name not in self.repositories:
            raise KeyError(
                f"Repository não encontrado: {name}"
            )

        return self.repositories[name]


    def begin(self):
        """
        Inicia unidade de trabalho.
        """

        self.session.open()

        self.transaction.begin()

        self.active = True


    def commit(self):
        """
        Confirma alterações.
        """

        if not self.active:
            raise RuntimeError(
                "UnitOfWork não iniciado."
            )

        self.transaction.commit()

        self.session.close()

        self.active = False


    def rollback(self):
        """
        Desfaz alterações.
        """

        if not self.active:
            return

        self.transaction.rollback()

        self.session.close()

        self.active = False


    def get_context(self):
        """
        Retorna contexto ativo.
        """

        return self.session.get_context()