from typing import Callable


class Transaction:
    """
    Transaction

    Controla uma operação transacional
    dentro da camada de persistência
    do KALATRACE.

    Responsável por:

    - commit;
    - rollback;
    - controle de estado.
    """

    def __init__(self):
        self.active = False

        self.committed = False

        self.rolled_back = False

        self.rollback_actions = []


    def begin(self):
        """
        Inicia uma transação.
        """

        if self.active:
            raise RuntimeError(
                "Transação já iniciada."
            )

        self.active = True

        self.committed = False

        self.rolled_back = False


    def add_rollback_action(
        self,
        action: Callable
    ):
        """
        Adiciona ação para rollback.
        """

        self.rollback_actions.append(
            action
        )


    def commit(self):
        """
        Confirma a transação.
        """

        if not self.active:
            raise RuntimeError(
                "Nenhuma transação ativa."
            )

        self.committed = True

        self.active = False

        self.rollback_actions.clear()


    def rollback(self):
        """
        Desfaz alterações realizadas.
        """

        if not self.active:
            raise RuntimeError(
                "Nenhuma transação ativa."
            )

        for action in reversed(
            self.rollback_actions
        ):
            action()

        self.rolled_back = True

        self.active = False

        self.rollback_actions.clear()


    def is_active(self) -> bool:
        """
        Verifica estado da transação.
        """

        return self.active