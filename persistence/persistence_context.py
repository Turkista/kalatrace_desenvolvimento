from typing import Dict, Any, Set


class PersistenceContext:
    """
    Persistence Context

    Mantém o estado das entidades durante
    o ciclo de persistência do KALATRACE.

    Responsável por controlar:

    - entidades carregadas;
    - entidades novas;
    - entidades modificadas;
    - entidades removidas.

    Não realiza armazenamento físico.
    Essa responsabilidade pertence aos repositories.
    """

    def __init__(self):
        self.entities: Dict[str, Any] = {}

        self.new_entities: Set[str] = set()

        self.modified_entities: Set[str] = set()

        self.removed_entities: Set[str] = set()


    def register_entity(
        self,
        entity_id: str,
        entity: Any
    ):
        """
        Registra uma entidade no contexto.
        """

        self.entities[entity_id] = entity


    def get_entity(
        self,
        entity_id: str
    ):
        """
        Recupera uma entidade existente
        no contexto.
        """

        return self.entities.get(entity_id)


    def add_new(
        self,
        entity_id: str
    ):
        """
        Marca entidade como nova.
        """

        self.new_entities.add(entity_id)


    def mark_modified(
        self,
        entity_id: str
    ):
        """
        Marca entidade como modificada.
        """

        self.modified_entities.add(entity_id)


    def mark_removed(
        self,
        entity_id: str
    ):
        """
        Marca entidade para remoção.
        """

        self.removed_entities.add(entity_id)


    def remove_entity(
        self,
        entity_id: str
    ):
        """
        Remove entidade do contexto.
        """

        if entity_id in self.entities:
            del self.entities[entity_id]


    def clear(self):
        """
        Limpa o contexto atual.
        """

        self.entities.clear()

        self.new_entities.clear()

        self.modified_entities.clear()

        self.removed_entities.clear()


    def get_pending_changes(self):
        """
        Retorna alterações pendentes.
        """

        return {
            "new": list(self.new_entities),
            "modified": list(
                self.modified_entities
            ),
            "removed": list(
                self.removed_entities
            )
        }