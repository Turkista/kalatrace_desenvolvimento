from __future__ import annotations


from typing import (
    List,
    Dict,
    Any,
    Optional,
)


from datetime import (
    datetime,
    UTC,
)



class Path:
    """
    Representa um caminho dentro
    de um grafo KALATRACE.


    Um Path contém:

    - sequência de Nodes;
    - sequência de Edges;
    - metadados do percurso.


    Não contém regras científicas.

    A interpretação epistemológica
    pertence às camadas superiores.
    """


    def __init__(
        self,
        path_id: str,
        nodes: Optional[
            List[str]
        ] = None,
        edges: Optional[
            List[str]
        ] = None,
    ) -> None:
        """
        Inicializa um caminho.


        Raises:

            ValueError:
                Caso path_id seja inválido.
        """


        if not path_id:

            raise ValueError(
                "path_id cannot be empty."
            )



        self.path_id = path_id



        self.nodes = (
            list(nodes)
            if nodes is not None
            else []
        )



        self.edges = (
            list(edges)
            if edges is not None
            else []
        )



        self.properties: Dict[
            str,
            Any
        ] = {}



        self.created_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )



    # ==========================================================
    # 1. ADICIONAR NODE AO CAMINHO
    # ==========================================================


    def add_node(
        self,
        node_id: str,
    ) -> None:
        """
        Adiciona um Node ao caminho.
        """


        if not node_id:

            raise ValueError(
                "node_id cannot be empty."
            )


        self.nodes.append(
            node_id
        )



    # ==========================================================
    # 2. ADICIONAR EDGE AO CAMINHO
    # ==========================================================


    def add_edge(
        self,
        edge_id: str,
    ) -> None:
        """
        Adiciona uma relação
        ao caminho.
        """


        if not edge_id:

            raise ValueError(
                "edge_id cannot be empty."
            )


        self.edges.append(
            edge_id
        )



    # ==========================================================
    # 3. REMOVER NODE
    # ==========================================================


    def remove_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove um Node do caminho.


        Returns:

            bool:
                True se removido.
        """


        if node_id not in self.nodes:

            return False



        self.nodes.remove(
            node_id
        )


        return True
    # ==========================================================
    # 4. REMOVER EDGE
    # ==========================================================


    def remove_edge(
        self,
        edge_id: str,
    ) -> bool:
        """
        Remove uma relação
        do caminho.


        Returns:

            bool:
                True se removida.
        """


        if edge_id not in self.edges:

            return False



        self.edges.remove(
            edge_id
        )


        return True




    # ==========================================================
    # 5. TAMANHO DO CAMINHO
    # ==========================================================


    def length(
        self,
    ) -> int:
        """
        Retorna quantidade
        de Nodes do caminho.
        """


        return len(
            self.nodes
        )




    # ==========================================================
    # 6. ADICIONAR PROPRIEDADE
    # ==========================================================


    def add_property(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Adiciona metadados
        ao caminho.
        """


        if not key:

            raise ValueError(
                "property key cannot be empty."
            )


        self.properties[key] = value




    # ==========================================================
    # 7. OBTER PROPRIEDADE
    # ==========================================================


    def get_property(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Recupera uma propriedade.
        """


        return self.properties.get(
            key,
            default,
        )




    # ==========================================================
    # 8. ATUALIZAR PROPRIEDADES
    # ==========================================================


    def update_properties(
        self,
        values: Dict[str, Any],
    ) -> None:
        """
        Atualiza múltiplas propriedades.
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
    # 9. VERIFICAR EXISTÊNCIA DE NODE
    # ==========================================================


    def contains_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Verifica se um Node
        pertence ao caminho.
        """


        return (
            node_id
            in
            self.nodes
        )




    # ==========================================================
    # 10. VERIFICAR EXISTÊNCIA DE EDGE
    # ==========================================================


    def contains_edge(
        self,
        edge_id: str,
    ) -> bool:
        """
        Verifica se uma relação
        pertence ao caminho.
        """


        return (
            edge_id
            in
            self.edges
        )




    # ==========================================================
    # 11. PRIMEIRO NODE
    # ==========================================================


    def first_node(
        self,
    ) -> Optional[str]:
        """
        Retorna o primeiro Node
        do caminho.
        """


        if not self.nodes:

            return None


        return self.nodes[0]




    # ==========================================================
    # 12. ÚLTIMO NODE
    # ==========================================================


    def last_node(
        self,
    ) -> Optional[str]:
        """
        Retorna o último Node
        do caminho.
        """


        if not self.nodes:

            return None


        return self.nodes[-1]




    # ==========================================================
    # 13. EXPORTAR PATH
    # ==========================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Converte o caminho
        para estrutura serializável.
        """


        return {

            "path_id":
                self.path_id,


            "nodes":
                list(
                    self.nodes
                ),


            "edges":
                list(
                    self.edges
                ),


            "properties":
                dict(
                    self.properties
                ),


            "created_at":
                self.created_at,

        }
    # ==========================================================
    # 14. VALIDAR PATH
    # ==========================================================


    def validate(
        self,
    ) -> bool:
        """
        Validação estrutural básica
        do caminho.


        Não valida:

        - existência real dos Nodes;
        - existência real dos Edges;
        - validade epistemológica.


        Essas verificações pertencem
        ao Graph Validator.
        """


        if not self.path_id:

            return False



        if not self.nodes:

            return False



        return True




    # ==========================================================
    # 15. COMPARAR PATHS
    # ==========================================================


    def equals(
        self,
        other: Any,
    ) -> bool:
        """
        Verifica se dois caminhos
        possuem o mesmo identificador.
        """


        if not isinstance(
            other,
            Path,
        ):

            return False



        return (

            self.path_id
            ==
            other.path_id

        )




    # ==========================================================
    # 16. COPIAR PATH
    # ==========================================================


    def copy(
        self,
    ) -> Path:
        """
        Cria uma cópia independente
        do caminho.
        """


        return Path(

            path_id=self.path_id,

            nodes=list(
                self.nodes
            ),

            edges=list(
                self.edges
            ),

        )




    # ==========================================================
    # 17. CONTAGEM DE ELEMENTOS
    # ==========================================================


    def stats(
        self,
    ) -> Dict[str, int]:
        """
        Retorna estatísticas
        básicas do caminho.
        """


        return {

            "nodes":
                len(
                    self.nodes
                ),


            "edges":
                len(
                    self.edges
                ),

        }




    # ==========================================================
    # 18. REPRESENTAÇÃO
    # ==========================================================


    def __repr__(
        self,
    ) -> str:
        """
        Representação textual
        do Path.
        """


        return (

            f"Path("
            f"id={self.path_id}, "
            f"nodes={len(self.nodes)}, "
            f"edges={len(self.edges)}"
            f")"

        )