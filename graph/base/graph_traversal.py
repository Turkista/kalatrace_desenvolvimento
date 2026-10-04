from __future__ import annotations


from collections import deque


from typing import (
    List,
    Set,
    Optional,
)


from graph.base.graph import Graph
from graph.base.node import Node
from graph.base.path import Path



class GraphTraversal:
    """
    Motor de navegação estrutural
    dos grafos KALATRACE.

    Responsável por:

    - explorar grafos;
    - encontrar vizinhos;
    - executar BFS;
    - executar DFS;
    - encontrar caminhos.

    Não possui regras epistemológicas.

    Camadas superiores:

    - Discovery Engine
    - Reasoning Engine
    - Knowledge Evolution Engine

    utilizam este componente.
    """



    def __init__(
        self,
        graph: Graph,
    ) -> None:
        """
        Inicializa o navegador.
        """

        if not isinstance(
            graph,
            Graph,
        ):
            raise TypeError(
                "graph must be an instance of Graph."
            )


        self.graph = graph



    # ==========================================================
    # 1. VIZINHOS
    # ==========================================================

    def neighbors(
        self,
        node_id: str,
        relation_type: Optional[str] = None,
    ) -> List[Node]:
        """
        Retorna nós conectados.

        relation_type:
            Opcionalmente filtra
            o tipo da relação.
        """

        result = []
        visited = set()


        for edge in self.graph.edges.values():

            if (
                relation_type is not None
                and
                edge.relation_type != relation_type
            ):
                continue


            neighbor_id = None


            if edge.source_id == node_id:

                neighbor_id = edge.target_id


            elif edge.target_id == node_id:

                neighbor_id = edge.source_id



            if neighbor_id:

                if neighbor_id not in visited:

                    node = self.graph.get_node(
                        neighbor_id
                    )

                    if node:

                        result.append(node)

                        visited.add(
                            neighbor_id
                        )


        return result



    # ==========================================================
    # 2. VIZINHOS DE SAÍDA
    # ==========================================================

    def outgoing_neighbors(
        self,
        node_id: str,
        relation_type: Optional[str] = None,
    ) -> List[Node]:
        """
        Retorna relações direcionadas
        de saída.
        """

        result = []


        for edge in self.graph.edges.values():

            if edge.source_id != node_id:

                continue


            if (
                relation_type
                and
                edge.relation_type != relation_type
            ):
                continue



            node = self.graph.get_node(
                edge.target_id
            )


            if node:

                result.append(node)


        return result



    # ==========================================================
    # 3. VIZINHOS DE ENTRADA
    # ==========================================================

    def incoming_neighbors(
        self,
        node_id: str,
        relation_type: Optional[str] = None,
    ) -> List[Node]:
        """
        Retorna nós que apontam
        para determinado nó.
        """

        result = []


        for edge in self.graph.edges.values():

            if edge.target_id != node_id:

                continue


            if (
                relation_type
                and
                edge.relation_type != relation_type
            ):
                continue



            node = self.graph.get_node(
                edge.source_id
            )


            if node:

                result.append(node)


        return result



    # ==========================================================
    # 4. BFS
    # ==========================================================

    def breadth_first_search(
        self,
        start_node_id: str,
        max_depth: Optional[int] = None,
    ) -> List[Node]:
        """
        Busca em largura.
        """

        if not self.graph.has_node(
            start_node_id
        ):
            return []


        visited: Set[str] = set()

        queue = deque(
            [
                (
                    start_node_id,
                    0,
                )
            ]
        )


        result = []


        while queue:

            current_id, depth = queue.popleft()


            if current_id in visited:

                continue


            visited.add(
                current_id
            )


            node = self.graph.get_node(
                current_id
            )


            if node:

                result.append(node)



            if (
                max_depth is not None
                and
                depth >= max_depth
            ):

                continue



            for neighbor in self.outgoing_neighbors(
                current_id
            ):

                if neighbor.node_id not in visited:

                    queue.append(
                        (
                            neighbor.node_id,
                            depth + 1,
                        )
                    )


        return result



    # ==========================================================
    # 5. DFS
    # ==========================================================

    def depth_first_search(
        self,
        start_node_id: str,
        max_depth: Optional[int] = None,
    ) -> List[Node]:
        """
        Busca em profundidade.
        """

        if not self.graph.has_node(
            start_node_id
        ):
            return []


        visited = set()

        stack = [
            (
                start_node_id,
                0,
            )
        ]


        result = []


        while stack:

            current_id, depth = stack.pop()


            if current_id in visited:

                continue


            visited.add(
                current_id
            )


            node = self.graph.get_node(
                current_id
            )


            if node:

                result.append(node)



            if (
                max_depth is not None
                and
                depth >= max_depth
            ):

                continue



            neighbors = self.outgoing_neighbors(
                current_id
            )


            for neighbor in reversed(neighbors):

                if neighbor.node_id not in visited:

                    stack.append(
                        (
                            neighbor.node_id,
                            depth + 1,
                        )
                    )


        return result



    # ==========================================================
    # 6. ENCONTRAR CAMINHO
    # ==========================================================

    def find_path(
        self,
        start_node_id: str,
        target_node_id: str,
    ) -> Optional[Path]:
        """
        Localiza caminho mínimo
        entre dois nós.
        """

        if (
            not self.graph.has_node(start_node_id)
            or
            not self.graph.has_node(target_node_id)
        ):
            return None



        queue = deque()

        queue.append(
            (
                start_node_id,
                [start_node_id],
                [],
            )
        )


        visited = set()



        while queue:

            current_id, nodes, edges = queue.popleft()


            if current_id == target_node_id:

                return Path(
                    path_id=(
                        f"{start_node_id}"
                        f"_TO_"
                        f"{target_node_id}"
                    ),
                    nodes=nodes,
                    edges=edges,
                )



            if current_id in visited:

                continue


            visited.add(
                current_id
            )



            for edge in self.graph.edges.values():

                if edge.source_id != current_id:

                    continue



                if edge.target_id in visited:

                    continue



                queue.append(
                    (
                        edge.target_id,
                        nodes + [
                            edge.target_id
                        ],
                        edges + [
                            edge.edge_id
                        ],
                    )
                )


        return None



    # ==========================================================
    # 7. CONECTIVIDADE
    # ==========================================================

    def is_connected(
        self,
        source_node_id: str,
        target_node_id: str,
    ) -> bool:
        """
        Verifica existência
        de caminho.
        """

        return (
            self.find_path(
                source_node_id,
                target_node_id,
            )
            is not None
        )



    # ==========================================================
    # 8. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        stats = self.graph.stats()


        return (
            "GraphTraversal("
            f"graph='{stats['name']}', "
            f"nodes={stats['nodes']}, "
            f"edges={stats['edges']}"
            ")"
        )