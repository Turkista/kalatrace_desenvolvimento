from __future__ import annotations


from typing import (
    Any,
    Dict,
    Optional,
)


from datetime import (
    datetime,
    UTC,
)



class Edge:
    """
    Classe base para todas as relações
    dentro dos grafos do KALATRACE.

    Um Edge conecta dois Nodes.

    Exemplos de relações:

    - SUPPORTS
    - CONTRADICTS
    - RELATED_TO
    - CAUSES
    - DERIVED_FROM
    - VALIDATED_BY

    O Edge representa apenas a estrutura
    da relação.

    Regras epistemológicas pertencem
    às camadas superiores.
    """



    def __init__(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Inicializa uma relação do grafo.

        Raises:

            ValueError:
                Caso campos essenciais
                estejam ausentes.
        """


        if not edge_id:
            raise ValueError(
                "edge_id cannot be empty."
            )


        if not source_id:
            raise ValueError(
                "source_id cannot be empty."
            )


        if not target_id:
            raise ValueError(
                "target_id cannot be empty."
            )


        if not relation_type:
            raise ValueError(
                "relation_type cannot be empty."
            )


        self.edge_id = edge_id


        self.source_id = source_id


        self.target_id = target_id


        self.relation_type = relation_type


        self.properties = (
            dict(properties)
            if properties is not None
            else {}
        )


        self.created_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )
    # ==========================================================
    # 1. ADICIONAR PROPRIEDADE
    # ==========================================================

    def add_property(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Adiciona ou atualiza
        uma propriedade da relação.

        Properties são metadados livres.
        Regras epistemológicas não devem
        ser implementadas neste nível.
        """


        self.properties[key] = value



    # ==========================================================
    # 2. OBTER PROPRIEDADE
    # ==========================================================

    def get_property(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Recupera uma propriedade
        específica da relação.
        """


        return self.properties.get(
            key,
            default,
        )



    # ==========================================================
    # 3. REMOVER PROPRIEDADE
    # ==========================================================

    def remove_property(
        self,
        key: str,
    ) -> bool:
        """
        Remove uma propriedade
        caso exista.

        Returns:

            bool:
                True caso removida.
                False caso inexistente.
        """


        if key in self.properties:

            del self.properties[key]

            return True


        return False



    # ==========================================================
    # 4. ATUALIZAR PROPRIEDADES
    # ==========================================================

    def update_properties(
        self,
        values: Dict[str, Any],
    ) -> None:
        """
        Atualiza várias propriedades
        da relação.
        """


        if not isinstance(
            values,
            dict,
        ):
            raise TypeError(
                "values must be a dictionary."
            )


        self.properties.update(
            values
        )



    # ==========================================================
    # 5. VERIFICAR TIPO DE RELAÇÃO
    # ==========================================================

    def is_relation(
        self,
        relation_type: str,
    ) -> bool:
        """
        Verifica se a relação
        pertence a determinado tipo.
        """


        return (
            self.relation_type
            ==
            relation_type
        )



    # ==========================================================
    # 6. ALTERAR RELAÇÃO
    # ==========================================================

    def change_relation(
        self,
        new_relation: str,
    ) -> None:
        """
        Modifica o tipo da relação.

        Útil quando novas evidências
        alteram a interpretação.

        A decisão epistemológica
        deve ocorrer em camadas superiores.
        """


        if not new_relation:
            raise ValueError(
                "new_relation cannot be empty."
            )


        self.relation_type = (
            new_relation
        )
    # ==========================================================
    # 7. EXPORTAR EDGE
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Converte a relação para
        estrutura serializável.

        Usado por:

        - APIs;
        - persistência;
        - auditoria;
        - exportação.
        """


        return {

            "edge_id":
                self.edge_id,


            "source_id":
                self.source_id,


            "target_id":
                self.target_id,


            "relation_type":
                self.relation_type,


            "properties":
                dict(
                    self.properties
                ),


            "created_at":
                self.created_at,

        }



    # ==========================================================
    # 8. VALIDAR EDGE
    # ==========================================================

    def validate(
        self,
    ) -> bool:
        """
        Validação mínima
        de integridade estrutural
        da relação.

        Não avalia:

        - qualidade da relação;
        - força epistemológica;
        - validade científica.
        """


        if not self.edge_id:

            return False


        if not self.source_id:

            return False


        if not self.target_id:

            return False


        if not self.relation_type:

            return False


        if not isinstance(
            self.properties,
            dict,
        ):

            return False


        return True



    # ==========================================================
    # 9. COMPARAR EDGES
    # ==========================================================

    def equals(
        self,
        other: Any,
    ) -> bool:
        """
        Verifica se duas relações
        representam a mesma entidade.
        """


        if not isinstance(
            other,
            Edge,
        ):
            return False


        return (
            self.edge_id
            ==
            other.edge_id
        )



    # ==========================================================
    # 10. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Representação técnica
        para debugging.
        """


        return (

            f"Edge("
            f"id={self.edge_id}, "
            f"{self.source_id} "
            f"--{self.relation_type}--> "
            f"{self.target_id}"
            f")"

        )