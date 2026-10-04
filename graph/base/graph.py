from __future__ import annotations


from typing import (
    Dict,
    List,
    Any,
    Optional,
)


from graph.base.node import Node
from graph.base.edge import Edge
from graph.base.path import Path



class Graph:
    """
    Classe base de grafos KALATRACE.

    Responsável pela infraestrutura
    de armazenamento e manipulação de:

    - Nodes
    - Edges
    - Paths


    Não contém lógica epistemológica.

    Regras científicas pertencem
    às camadas superiores:

    - KnowledgeGraph
    - DiscoveryGraph
    - OntologyGraph
    - ValidationEngine
    - Governance


    Este componente representa
    apenas a estrutura relacional.
    """



    def __init__(
        self,
        graph_id: str,
        name: str,
    ) -> None:
        """
        Inicializa um grafo.

        Raises:

            ValueError:
                Caso identificadores
                essenciais estejam vazios.
        """


        if not graph_id:

            raise ValueError(
                "graph_id cannot be empty."
            )


        if not name:

            raise ValueError(
                "name cannot be empty."
            )



        self.graph_id = graph_id


        self.name = name



        self.nodes: Dict[
            str,
            Node
        ] = {}



        self.edges: Dict[
            str,
            Edge
        ] = {}



        self.paths: Dict[
            str,
            Path
        ] = {}



    # ==========================================================
    # 1. ADICIONAR NODE
    # ==========================================================


    def add_node(
        self,
        node: Node,
    ) -> str:
        """
        Adiciona um Node ao grafo.
        """


        if not isinstance(
            node,
            Node,
        ):

            raise TypeError(
                "node must be an instance of Node."
            )



        self.nodes[
            node.node_id
        ] = node



        return node.node_id



    # ==========================================================
    # 2. OBTER NODE
    # ==========================================================


    def get_node(
        self,
        node_id: str,
    ) -> Optional[Node]:
        """
        Recupera um Node pelo identificador.
        """


        return self.nodes.get(
            node_id
        )



    # ==========================================================
    # 3. VERIFICAR NODE
    # ==========================================================


    def has_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Verifica existência de um Node.
        """


        return (
            node_id
            in
            self.nodes
        )



    # ==========================================================
    # 4. REMOVER NODE
    # ==========================================================


    def remove_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Remove um Node e todas
        as relações conectadas.


        Returns:

            bool:
                True se removido.
        """


        if node_id not in self.nodes:

            return False



        del self.nodes[
            node_id
        ]



        edges_to_remove = [

            edge_id

            for edge_id, edge

            in self.edges.items()

            if (

                edge.source_id == node_id

                or

                edge.target_id == node_id

            )

        ]



        for edge_id in edges_to_remove:

            del self.edges[
                edge_id
            ]



        return True
    # ==========================================================
    # 5. ADICIONAR EDGE
    # ==========================================================


    def add_edge(
        self,
        edge: Edge,
    ) -> str:
        """
        Adiciona uma relação ao grafo.

        O grafo garante que
        origem e destino existam.
        """


        if not isinstance(
            edge,
            Edge,
        ):

            raise TypeError(
                "edge must be an instance of Edge."
            )



        if not self.has_node(
            edge.source_id
        ):

            raise ValueError(
                f"Source node '{edge.source_id}' does not exist."
            )



        if not self.has_node(
            edge.target_id
        ):

            raise ValueError(
                f"Target node '{edge.target_id}' does not exist."
            )



        self.edges[
            edge.edge_id
        ] = edge



        return edge.edge_id




    # ==========================================================
    # 6. OBTER EDGE
    # ==========================================================


    def get_edge(
        self,
        edge_id: str,
    ) -> Optional[Edge]:
        """
        Recupera uma relação pelo ID.
        """


        return self.edges.get(
            edge_id
        )




    # ==========================================================
    # 7. VERIFICAR EDGE
    # ==========================================================


    def has_edge(
        self,
        edge_id: str,
    ) -> bool:
        """
        Verifica se uma relação existe.
        """


        return (
            edge_id
            in
            self.edges
        )




    # ==========================================================
    # 8. REMOVER EDGE
    # ==========================================================


    def remove_edge(
        self,
        edge_id: str,
    ) -> bool:
        """
        Remove uma relação.


        Returns:

            bool:
                True caso removida.
        """


        if edge_id not in self.edges:

            return False



        del self.edges[
            edge_id
        ]



        return True




    # ==========================================================
    # 9. BUSCAR RELAÇÕES DE UM NODE
    # ==========================================================


    def get_edges_for_node(
        self,
        node_id: str,
    ) -> List[Edge]:
        """
        Retorna todas as relações
        associadas a um Node.
        """


        return [

            edge

            for edge

            in self.edges.values()

            if (

                edge.source_id == node_id

                or

                edge.target_id == node_id

            )

        ]




    # ==========================================================
    # 10. ADICIONAR PATH
    # ==========================================================


    def add_path(
        self,
        path: Path,
    ) -> str:
        """
        Adiciona um caminho ao grafo.
        """


        if not isinstance(
            path,
            Path,
        ):

            raise TypeError(
                "path must be an instance of Path."
            )



        self.paths[
            path.path_id
        ] = path



        return path.path_id




    # ==========================================================
    # 11. OBTER PATH
    # ==========================================================


    def get_path(
        self,
        path_id: str,
    ) -> Optional[Path]:
        """
        Recupera um caminho pelo ID.
        """


        return self.paths.get(
            path_id
        )




    # ==========================================================
    # 12. REMOVER PATH
    # ==========================================================


    def remove_path(
        self,
        path_id: str,
    ) -> bool:
        """
        Remove um caminho.
        """


        if path_id not in self.paths:

            return False



        del self.paths[
            path_id
        ]



        return True




    # ==========================================================
    # 13. LISTAR NODES
    # ==========================================================


    def list_nodes(
        self,
    ) -> List[Node]:
        """
        Retorna todos os Nodes.
        """


        return list(
            self.nodes.values()
        )




    # ==========================================================
    # 14. LISTAR EDGES
    # ==========================================================


    def list_edges(
        self,
    ) -> List[Edge]:
        """
        Retorna todas as relações.
        """


        return list(
            self.edges.values()
        )




    # ==========================================================
    # 15. LISTAR PATHS
    # ==========================================================


    def list_paths(
        self,
    ) -> List[Path]:
        """
        Retorna todos os caminhos.
        """


        return list(
            self.paths.values()
        )
    # ==========================================================
    # 16. ESTATÍSTICAS DO GRAFO
    # ==========================================================


    def stats(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna métricas básicas
        do grafo.
        """


        return {

            "graph_id":
                self.graph_id,


            "name":
                self.name,


            "nodes":
                len(
                    self.nodes
                ),


            "edges":
                len(
                    self.edges
                ),


            "paths":
                len(
                    self.paths
                ),

        }




    # ==========================================================
    # 17. EXPORTAR GRAFO
    # ==========================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Exporta o grafo para
        estrutura serializável.


        Usado por:

        - APIs
        - Persistência
        - Auditoria
        - Backup
        - Versionamento
        """


        return {

            "graph_id":
                self.graph_id,


            "name":
                self.name,


            "nodes":

                [

                    node.to_dict()

                    for node
                    in self.nodes.values()

                ],


            "edges":

                [

                    edge.to_dict()

                    for edge
                    in self.edges.values()

                ],


            "paths":

                [

                    path.to_dict()

                    for path
                    in self.paths.values()

                ],

        }




    # ==========================================================
    # 18. LIMPAR GRAFO
    # ==========================================================


    def clear(
        self,
    ) -> None:
        """
        Remove todo conteúdo
        armazenado no grafo.
        """


        self.nodes.clear()


        self.edges.clear()


        self.paths.clear()




    # ==========================================================
    # 19. VALIDAR GRAFO
    # ==========================================================


    def validate(
        self,
    ) -> bool:
        """
        Executa validação estrutural
        básica do grafo.


        Não valida:

        - evidência científica;
        - confiança;
        - consistência epistemológica.


        Essas regras pertencem
        aos Validators superiores.
        """


        for node in self.nodes.values():

            if not node.validate():

                return False



        for edge in self.edges.values():

            if not edge.validate():

                return False



        for path in self.paths.values():

            if not path.validate():

                return False



        return True




    # ==========================================================
    # 20. BUSCAR NODES POR TIPO
    # ==========================================================


    def find_nodes_by_type(
        self,
        node_type: str,
    ) -> List[Node]:
        """
        Retorna Nodes de determinado tipo.
        """


        return [

            node

            for node

            in self.nodes.values()

            if node.node_type == node_type

        ]




    # ==========================================================
    # 21. BUSCAR EDGES POR RELAÇÃO
    # ==========================================================


    def find_edges_by_relation(
        self,
        relation_type: str,
    ) -> List[Edge]:
        """
        Retorna relações
        de determinado tipo.
        """


        return [

            edge

            for edge

            in self.edges.values()

            if edge.relation_type == relation_type

        ]




    # ==========================================================
    # 22. GRAU DE CONEXÃO
    # ==========================================================


    def degree(
        self,
        node_id: str,
    ) -> int:
        """
        Retorna número de conexões
        de um Node.
        """


        return len(
            self.get_edges_for_node(
                node_id
            )
        )




    # ==========================================================
    # 23. NODES ISOLADOS
    # ==========================================================


    def isolated_nodes(
        self,
    ) -> List[Node]:
        """
        Retorna Nodes sem conexões.


        Útil para:

        - análise de qualidade;
        - detecção de conhecimento frágil;
        - governança.
        """


        return [

            node

            for node

            in self.nodes.values()

            if self.degree(
                node.node_id
            ) == 0

        ]




    # ==========================================================
    # 24. CONTAGEM DE RELAÇÕES
    # ==========================================================


    def relation_count(
        self,
        relation_type: str,
    ) -> int:
        """
        Conta relações específicas.
        """


        return len(
            self.find_edges_by_relation(
                relation_type
            )
        )




    # ==========================================================
    # 25. REPRESENTAÇÃO
    # ==========================================================


    def __repr__(
        self,
    ) -> str:
        """
        Representação textual
        do grafo.
        """


        stats = self.stats()


        return (

            f"Graph("
            f"id={stats['graph_id']}, "
            f"nodes={stats['nodes']}, "
            f"edges={stats['edges']}, "
            f"paths={stats['paths']}"
            f")"

        )