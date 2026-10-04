from typing import Dict, Any


class QueryBuilder:
    """
    Query Builder

    Responsável pela construção
    de consultas abstratas
    da camada de persistência.
    """

    def __init__(self):
        self.entity = None

        self.filters: Dict[
            str,
            Any
        ] = {}

        self.parameters: Dict[
            str,
            Any
        ] = {}


    def from_entity(
        self,
        entity_name: str
    ):
        """
        Define entidade alvo.
        """

        self.entity = entity_name

        return self


    def where(
        self,
        field: str,
        value: Any
    ):
        """
        Adiciona filtro.
        """

        self.filters[field] = value

        return self


    def add_parameter(
        self,
        name: str,
        value: Any
    ):
        """
        Adiciona parâmetro.
        """

        self.parameters[name] = value

        return self


    def build(self):
        """
        Gera representação
        da consulta.
        """

        return {
            "entity": self.entity,
            "filters": self.filters,
            "parameters": self.parameters
        }


    def clear(self):
        """
        Limpa consulta atual.
        """

        self.entity = None

        self.filters.clear()

        self.parameters.clear()