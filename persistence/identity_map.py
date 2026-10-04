from typing import Dict, Any


class IdentityMap:
    """
    Identity Map

    Mantém uma única instância
    de cada entidade carregada
    durante uma sessão.
    """

    def __init__(self):
        self.entities: Dict[
            str,
            Any
        ] = {}


    def add(
        self,
        entity_id: str,
        entity: Any
    ):
        """
        Registra uma entidade.
        """

        self.entities[
            entity_id
        ] = entity


    def get(
        self,
        entity_id: str
    ):
        """
        Recupera entidade existente.
        """

        return self.entities.get(
            entity_id
        )


    def contains(
        self,
        entity_id: str
    ) -> bool:
        """
        Verifica se entidade existe.
        """

        return entity_id in self.entities


    def remove(
        self,
        entity_id: str
    ):
        """
        Remove entidade.
        """

        if entity_id in self.entities:
            del self.entities[
                entity_id
            ]


    def clear(self):
        """
        Limpa mapa de identidade.
        """

        self.entities.clear()


    def size(self) -> int:
        """
        Retorna quantidade de entidades.
        """

        return len(
            self.entities
        )