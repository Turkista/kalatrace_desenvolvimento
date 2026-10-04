from __future__ import annotations


from typing import (
    Optional,
    List,
)


from graph.base.graph import Graph
from graph.base.node import Node
from graph.base.edge import Edge
from graph.base.path import Path



class GraphBuilder:
    """
    Construtor de grafos KALATRACE.

    Responsável por:

    - criar Nodes;
    - criar Edges;
    - criar Paths;
    - garantir consistência estrutural básica.

    O GraphBuilder NÃO possui regras epistemológicas.

    Regras científicas pertencem às camadas superiores:

    - KnowledgeGraph
    - DiscoveryGraph
    - OntologyGraph
    - ValidationEngine
    """



    def __init__(
        self,
        graph: Optional[Graph] = None,
    ) -> None:
        """
        Inicializa o builder.

        Caso nenhum grafo seja informado,
        cria um grafo vazio padrão.
        """


        self.graph = (
            graph
            if graph is not None
            else Graph(
                graph_id="default",
                name="Default Graph",
            )
        )



    # ==========================================================
    # 1. OBTER GRAFO
    # ==========================================================

    def get_graph(
        self,
    ) -> Graph:
        """
        Retorna o grafo atual.
        """

        return self.graph



    # ==========================================================
    # 2. ADICIONAR NODE
    # ==========================================================

    def add_node(
        self,
        node: Node,
    ) -> Node:
        """
        Adiciona um Node.

        Caso já exista um Node
        com o mesmo ID, retorna
        o existente.
        """


        if not isinstance(
            node,
            Node,
        ):
            raise TypeError(
                "node must be an instance of Node."
            )


        existing = self.graph.get_node(
            node.node_id
        )


        if existing:
            return existing



        self.graph.add_node(
            node
        )


        return node



    # ==========================================================
    # 3. ADICIONAR EDGE
    # ==========================================================

    def add_edge(
        self,
        edge: Edge,
    ) -> Edge:
        """
        Adiciona uma relação.
        """


        if not isinstance(
            edge,
            Edge,
        ):
            raise TypeError(
                "edge must be an instance of Edge."
            )


        existing = self.graph.get_edge(
            edge.edge_id
        )


        if existing:
            return existing



        self.graph.add_edge(
            edge
        )


        return edge



    # ==========================================================
    # 4. ADICIONAR PATH
    # ==========================================================

    def add_path(
        self,
        path: Path,
    ) -> Path:
        """
        Adiciona um caminho.
        """


        if not isinstance(
            path,
            Path,
        ):
            raise TypeError(
                "path must be an instance of Path."
            )


        existing = self.graph.get_path(
            path.path_id
        )


        if existing:
            return existing



        self.graph.add_path(
            path
        )


        return path



    # ==========================================================
    # 5. CONECTAR NODES
    # ==========================================================

    def connect(
        self,
        source_node: Node,
        target_node: Node,
        relation_type: str,
        edge_id: Optional[str] = None,
    ) -> Edge:
        """
        Cria uma relação entre dois Nodes.

        Adiciona automaticamente
        os Nodes caso ainda não existam.
        """


        if not relation_type:

            raise ValueError(
                "relation_type cannot be empty."
            )


        self.add_node(
            source_node
        )


        self.add_node(
            target_node
        )



        if edge_id is None:

            edge_id = (
                f"{source_node.node_id}"
                f"__{relation_type}__"
                f"{target_node.node_id}"
            )



        edge = Edge(
            edge_id=edge_id,
            source_id=source_node.node_id,
            target_id=target_node.node_id,
            relation_type=relation_type,
        )



        return self.add_edge(
            edge
        )



    # ==========================================================
    # 6. CONSTRUIR PATH
    # ==========================================================

    def build_path(
        self,
        path_id: str,
        nodes: List[str],
        edges: List[str],
    ) -> Path:
        """
        Cria e registra um caminho.
        """


        if not path_id:

            raise ValueError(
                "path_id cannot be empty."
            )



        path = Path(
            path_id=path_id,
            nodes=nodes,
            edges=edges,
        )



        return self.add_path(
            path
        )



    # ==========================================================
    # 7. ADIÇÃO EM LOTE
    # ==========================================================

    def bulk_add_nodes(
        self,
        nodes: List[Node],
    ) -> int:
        """
        Adiciona múltiplos Nodes.
        """


        count = 0


        for node in nodes:

            self.add_node(
                node
            )

            count += 1



        return count



    def bulk_add_edges(
        self,
        edges: List[Edge],
    ) -> int:
        """
        Adiciona múltiplas relações.
        """


        count = 0


        for edge in edges:

            self.add_edge(
                edge
            )

            count += 1



        return count



    # ==========================================================
    # 8. RESETAR BUILDER
    # ==========================================================

    def reset(
        self,
        graph_id: str = "default",
        name: str = "Default Graph",
    ) -> None:
        """
        Cria um novo grafo vazio.
        """


        self.graph = Graph(
            graph_id=graph_id,
            name=name,
        )



    # ==========================================================
    # 9. ESTATÍSTICAS
    # ==========================================================

    def stats(
        self,
    ):
        """
        Retorna métricas do grafo.
        """


        return self.graph.stats()



    # ==========================================================
    # 10. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        stats = self.graph.stats()


        return (
            "GraphBuilder("
            f"graph='{stats['name']}', "
            f"nodes={stats['nodes']}, "
            f"edges={stats['edges']}, "
            f"paths={stats['paths']}"
            ")"
        )