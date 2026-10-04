from typing import Dict

from persistence.repository import (
    Repository
)


class RepositoryFactory:
    """
    Repository Factory

    Responsável pela criação e
    gerenciamento de repositories
    do KALATRACE.
    """

    def __init__(self):
        self.repositories: Dict[
            str,
            Repository
        ] = {}


    def create(
        self,
        name: str
    ) -> Repository:
        """
        Cria ou recupera um repository.
        """

        if name in self.repositories:
            return self.repositories[name]

        repository = Repository()

        self.repositories[name] = repository

        return repository


    def get(
        self,
        name: str
    ):
        """
        Recupera repository existente.
        """

        if name not in self.repositories:
            raise KeyError(
                f"Repository não encontrado: {name}"
            )

        return self.repositories[name]


    def exists(
        self,
        name: str
    ) -> bool:
        """
        Verifica existência.
        """

        return name in self.repositories


    def remove(
        self,
        name: str
    ):
        """
        Remove repository.
        """

        if name in self.repositories:
            del self.repositories[name]


    def clear(self):
        """
        Limpa repositories.
        """

        self.repositories.clear()