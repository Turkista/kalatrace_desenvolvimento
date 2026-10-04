from typing import Dict, Any, List


class Repository:
    """
    Base Repository

    Classe base para todos os
    repositórios do KALATRACE.

    Responsável por abstrair
    operações de persistência.
    """

    def __init__(self):
        self.storage: Dict[str, Any] = {}


    def save(
        self,
        entity_id: str,
        entity: Any
    ):
        """
        Salva ou atualiza uma entidade.
        """

        self.storage[entity_id] = entity


    def find_by_id(
        self,
        entity_id: str
    ):
        """
        Busca entidade por identificador.
        """

        return self.storage.get(
            entity_id
        )


    def find_all(self) -> List[Any]:
        """
        Retorna todas as entidades.
        """

        return list(
            self.storage.values()
        )


    def exists(
        self,
        entity_id: str
    ) -> bool:
        """
        Verifica existência.
        """

        return entity_id in self.storage


    def delete(
        self,
        entity_id: str
    ):
        """
        Remove entidade.
        """

        if entity_id in self.storage:
            del self.storage[entity_id]


    def count(self) -> int:
        """
        Retorna quantidade de entidades.
        """

        return len(
            self.storage
        )