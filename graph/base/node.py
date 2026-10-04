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



class Node:
    """
    Classe base para todos os nós
    da arquitetura de grafos KALATRACE.

    Um Node representa uma entidade
    dentro do conhecimento.

    Exemplos:

    - IEC
    - Evidence
    - Hypothesis
    - Concept
    - Mechanism
    - Document

    O Node é uma estrutura genérica.
    Regras epistemológicas específicas
    pertencem às camadas superiores.
    """



    def __init__(
        self,
        node_id: str,
        node_type: str,
        label: str,
        properties: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Inicializa um nó do grafo.

        Raises:

            ValueError:
                Caso informações essenciais
                estejam ausentes.
        """


        if not node_id:
            raise ValueError(
                "node_id cannot be empty."
            )


        if not node_type:
            raise ValueError(
                "node_type cannot be empty."
            )


        if not label:
            raise ValueError(
                "label cannot be empty."
            )


        self.node_id = node_id


        self.node_type = node_type


        self.label = label


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
        uma propriedade do nó.

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
        do nó.
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
        Atualiza múltiplas propriedades
        simultaneamente.
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
    # 5. VERIFICAR TIPO
    # ==========================================================

    def is_type(
        self,
        node_type: str,
    ) -> bool:
        """
        Verifica se o nó pertence
        a determinado tipo.
        """


        return (
            self.node_type
            ==
            node_type
        )



    # ==========================================================
    # 6. EXPORTAR NODE
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Converte o Node para
        estrutura serializável.

        Usado por:

        - APIs;
        - persistência;
        - auditoria;
        - exportação.
        """


        return {

            "node_id":
                self.node_id,


            "node_type":
                self.node_type,


            "label":
                self.label,


            "properties":
                dict(
                    self.properties
                ),


            "created_at":
                self.created_at,

        }
    # ==========================================================
    # 7. COMPARAR NÓS
    # ==========================================================

    def equals(
        self,
        other: Any,
    ) -> bool:
        """
        Verifica se dois nós
        representam a mesma entidade.

        A comparação utiliza apenas
        o identificador único.
        """


        if not isinstance(
            other,
            Node,
        ):
            return False


        return (
            self.node_id
            ==
            other.node_id
        )



    # ==========================================================
    # 8. VALIDAR NODE
    # ==========================================================

    def validate(
        self,
    ) -> bool:
        """
        Executa validação mínima
        de integridade estrutural.

        Esta validação não avalia
        qualidade epistemológica.

        Retorna:

            bool:
                True quando a estrutura
                mínima está válida.
        """


        if not self.node_id:
            return False


        if not self.node_type:
            return False


        if not self.label:
            return False


        if not isinstance(
            self.properties,
            dict,
        ):
            return False


        return True



    # ==========================================================
    # 9. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Representação técnica
        do objeto para debugging.
        """


        return (

            f"Node("
            f"id={self.node_id}, "
            f"type={self.node_type}, "
            f"label={self.label}"
            f")"

        )
