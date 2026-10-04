from typing import Dict, Any


class Mapper:
    """
    Mapper

    Responsável pela conversão entre
    entidades do domínio e estruturas
    persistíveis.
    """

    def to_storage(
        self,
        entity: Any
    ) -> Dict[str, Any]:
        """
        Converte entidade para formato
        persistível.
        """

        if hasattr(
            entity,
            "__dict__"
        ):
            return entity.__dict__

        raise TypeError(
            "Entidade não possui representação persistível."
        )


    def from_storage(
        self,
        data: Dict[str, Any],
        entity_class
    ):
        """
        Reconstrói entidade a partir
        de dados persistidos.
        """

        entity = entity_class.__new__(
            entity_class
        )

        for key, value in data.items():
            setattr(
                entity,
                key,
                value
            )

        return entity


    def update_entity(
        self,
        entity: Any,
        data: Dict[str, Any]
    ):
        """
        Atualiza entidade existente.
        """

        for key, value in data.items():

            setattr(
                entity,
                key,
                value
            )

        return entity