from datetime import datetime, UTC
from typing import Dict, List, Optional, Any

from _archive.graph_knowledge.knowledge_node import KnowledgeNode
from _archive.graph_knowledge.knowledge_edge import KnowledgeEdge
from _archive.graph_knowledge.evidence_node import EvidenceNode
from _archive.graph_knowledge.knowledge_path import KnowledgePath



class KnowledgeGraph:
    """
    Grafo principal de conhecimento
    científico do KALATRACE.

    Responsável por gerenciar:

    - KnowledgeNodes
    - EvidenceNodes
    - KnowledgeEdges
    - KnowledgePaths


    Não contém regras de domínio.
    Apenas organiza relações epistemológicas.
    """


    def __init__(
        self,
        graph_id: str = "knowledge_graph",
        name: str = "Scientific Knowledge Graph"
    ):
        """
        Inicializa o grafo.
        """

        self.graph_id = graph_id

        self.name = name


        self.nodes: Dict[
            str,
            KnowledgeNode
        ] = {}


        self.edges: Dict[
            str,
            KnowledgeEdge
        ] = {}


        self.paths: Dict[
            str,
            KnowledgePath
        ] = {}


        self.metadata: Dict[
            str,
            Any
        ] = {}


        self.created_at = (
            datetime.now(UTC)
            .isoformat()
        )
    # ==========================================================
    # 1. ADICIONAR NÓ
    # ==========================================================

    def add_node(
        self,
        node: KnowledgeNode
    ) -> None:
        """
        Adiciona um KnowledgeNode ao grafo.

        EvidenceNode também é aceito,
        pois herda de KnowledgeNode.
        """

        if not isinstance(
            node,
            KnowledgeNode
        ):

            raise TypeError(
                "node must be an instance of KnowledgeNode."
            )


        if node.node_id in self.nodes:

            raise ValueError(
                f"Nó '{node.node_id}' já existe."
            )


        self.nodes[
            node.node_id
        ] = node



    # ==========================================================
    # 2. OBTER NÓ
    # ==========================================================

    def get_node(
        self,
        node_id: str
    ) -> Optional[KnowledgeNode]:
        """
        Recupera um nó pelo identificador.
        """

        return self.nodes.get(
            node_id
        )



    # ==========================================================
    # 3. VERIFICAR EXISTÊNCIA DE NÓ
    # ==========================================================

    def has_node(
        self,
        node_id: str
    ) -> bool:
        """
        Verifica se um nó existe
        dentro do KnowledgeGraph.
        """

        return (
            node_id
            in
            self.nodes
        )



    # ==========================================================
    # 4. REMOVER NÓ
    # ==========================================================

    def remove_node(
        self,
        node_id: str
    ) -> None:
        """
        Remove um nó do grafo.

        Também remove relações
        associadas ao nó.
        """

        if node_id not in self.nodes:

            return


        del self.nodes[
            node_id
        ]


        edges_to_remove = []


        for edge_id, edge in self.edges.items():

            if (

                edge.source_id == node_id

                or

                edge.target_id == node_id

            ):

                edges_to_remove.append(
                    edge_id
                )


        for edge_id in edges_to_remove:

            del self.edges[
                edge_id
            ]



    # ==========================================================
    # 5. LISTAR NÓS
    # ==========================================================

    def list_nodes(
        self
    ) -> List[KnowledgeNode]:
        """
        Retorna todos os nós
        existentes no grafo.
        """

        return list(
            self.nodes.values()
        )



    # ==========================================================
    # 6. LISTAR EVIDÊNCIAS
    # ==========================================================

    def list_evidences(
        self
    ) -> List[EvidenceNode]:
        """
        Retorna somente EvidenceNodes.
        """

        return [

            node

            for node
            in self.nodes.values()

            if isinstance(
                node,
                EvidenceNode
            )

        ]



    # ==========================================================
    # 7. BUSCAR NÓS POR TIPO
    # ==========================================================

    def find_nodes_by_type(
        self,
        node_type: str
    ) -> List[KnowledgeNode]:
        """
        Retorna nós de determinado tipo.

        Exemplos:

        IEC

        Hypothesis

        Evidence

        Mechanism
        """

        return [

            node

            for node
            in self.nodes.values()

            if node.node_type == node_type

        ]



    # ==========================================================
    # 8. BUSCAR POR DOMÍNIO
    # ==========================================================

    def find_nodes_by_domain(
        self,
        domain: str
    ) -> List[KnowledgeNode]:
        """
        Retorna conhecimentos
        pertencentes a um domínio.
        """

        return [

            node

            for node
            in self.nodes.values()

            if getattr(
                node,
                "domain",
                None
            ) == domain

        ]
    # ==========================================================
    # 9. ADICIONAR RELAÇÃO
    # ==========================================================

    def add_edge(
        self,
        edge: KnowledgeEdge
    ) -> None:
        """
        Adiciona uma relação epistemológica
        ao KnowledgeGraph.
        """

        if not isinstance(
            edge,
            KnowledgeEdge
        ):

            raise TypeError(
                "edge must be an instance of KnowledgeEdge."
            )


        if edge.edge_id in self.edges:

            raise ValueError(
                f"Relação '{edge.edge_id}' já existe."
            )


        if not self.has_node(
            edge.source_id
        ):

            raise ValueError(
                f"Nó origem '{edge.source_id}' não encontrado."
            )


        if not self.has_node(
            edge.target_id
        ):

            raise ValueError(
                f"Nó destino '{edge.target_id}' não encontrado."
            )


        self.edges[
            edge.edge_id
        ] = edge



    # ==========================================================
    # 10. OBTER RELAÇÃO
    # ==========================================================

    def get_edge(
        self,
        edge_id: str
    ) -> Optional[KnowledgeEdge]:
        """
        Recupera uma relação
        pelo identificador.
        """

        return self.edges.get(
            edge_id
        )



    # ==========================================================
    # 11. VERIFICAR RELAÇÃO
    # ==========================================================

    def has_edge(
        self,
        edge_id: str
    ) -> bool:
        """
        Verifica se uma relação
        existe no grafo.
        """

        return (
            edge_id
            in
            self.edges
        )



    # ==========================================================
    # 12. REMOVER RELAÇÃO
    # ==========================================================

    def remove_edge(
        self,
        edge_id: str
    ) -> None:
        """
        Remove uma relação.
        """

        if edge_id in self.edges:

            del self.edges[
                edge_id
            ]



    # ==========================================================
    # 13. LISTAR RELAÇÕES
    # ==========================================================

    def list_edges(
        self
    ) -> List[KnowledgeEdge]:
        """
        Retorna todas as relações
        do grafo.
        """

        return list(
            self.edges.values()
        )



    # ==========================================================
    # 14. BUSCAR RELAÇÕES DE UM NÓ
    # ==========================================================

    def get_edges_for_node(
        self,
        node_id: str
    ) -> List[KnowledgeEdge]:
        """
        Retorna todas as relações
        conectadas a um nó.
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
    # 14a. VIZINHOS DIRETOS (portado de graph/knowledge_graph.py — T1.2a)
    # ==========================================================
    # Achado da T0.4: neighbors(), isolated_nodes() e low_confidence_edges()
    # existiam só na versão leve do grafo -- não são métodos "extras"
    # dispensáveis, isolated_nodes() em particular é chamado ativamente
    # por validation/validation_engine.py e curation/curation.py. Portados
    # aqui usando get_edges_for_node()/list_nodes(), já existentes nesta
    # classe, mantendo a mesma semântica da versão leve.

    def neighbors(
        self,
        node_id: str
    ) -> List[KnowledgeNode]:
        """
        Retorna nós vizinhos diretos (navegação cognitiva).
        """

        result = set()

        for edge in self.get_edges_for_node(node_id):
            if edge.source_id == node_id:
                result.add(edge.target_id)
            elif edge.target_id == node_id:
                result.add(edge.source_id)

        return [
            self.nodes[n]
            for n in result
            if n in self.nodes
        ]

    # ==========================================================
    # 14b. NÓS ISOLADOS (portado de graph/knowledge_graph.py — T1.2a)
    # ==========================================================

    def isolated_nodes(self) -> List[KnowledgeNode]:
        """
        Nós sem nenhuma conexão (lacunas epistemológicas).
        """

        connected = set()

        for edge in self.edges.values():
            connected.add(edge.source_id)
            connected.add(edge.target_id)

        return [
            self.nodes[node_id]
            for node_id in self.nodes
            if node_id not in connected
        ]

    # ==========================================================
    # 14c. RELAÇÕES DE BAIXA CONFIANÇA (portado — T1.2a)
    # ==========================================================

    def low_confidence_edges(
        self,
        threshold: float = 0.3
    ) -> List[KnowledgeEdge]:
        """
        Relações fracas -> candidatas a revisão.
        """

        return [
            edge
            for edge in self.edges.values()
            if edge.confidence < threshold
        ]

    # ==========================================================
    # 15. BUSCAR RELAÇÕES POR TIPO
    # ==========================================================

    def find_edges_by_relation(
        self,
        relation_type: str
    ) -> List[KnowledgeEdge]:
        """
        Retorna relações de determinado tipo.

        Exemplos:

        SUPPORTS

        CONTRADICTS

        DERIVED_FROM
        """

        return [

            edge

            for edge
            in self.edges.values()

            if edge.relation_type == relation_type

        ]



    # ==========================================================
    # 16. ADICIONAR KNOWLEDGE PATH
    # ==========================================================

    def add_path(
        self,
        path: KnowledgePath
    ) -> None:
        """
        Adiciona um caminho epistemológico.
        """

        if not isinstance(
            path,
            KnowledgePath
        ):

            raise TypeError(
                "path must be an instance of KnowledgePath."
            )


        if path.path_id in self.paths:

            raise ValueError(
                f"Path '{path.path_id}' já existe."
            )


        self.paths[
            path.path_id
        ] = path



    # ==========================================================
    # 17. OBTER PATH
    # ==========================================================

    def get_path(
        self,
        path_id: str
    ) -> Optional[KnowledgePath]:
        """
        Recupera um caminho
        pelo identificador.
        """

        return self.paths.get(
            path_id
        )



    # ==========================================================
    # 18. LISTAR PATHS
    # ==========================================================

    def list_paths(
        self
    ) -> List[KnowledgePath]:
        """
        Retorna todos os caminhos
        epistemológicos.
        """

        return list(
            self.paths.values()
        )



    # ==========================================================
    # 19. REMOVER PATH
    # ==========================================================

    def remove_path(
        self,
        path_id: str
    ) -> None:
        """
        Remove um caminho.
        """

        if path_id in self.paths:

            del self.paths[
                path_id
            ]
    # ==========================================================
    # 20. VALIDAR GRAFO
    # ==========================================================

    def validate(
        self
    ) -> bool:
        """
        Valida a integridade completa
        do KnowledgeGraph.

        Verifica:

        - Nodes válidos
        - Edges válidos
        - Paths válidos
        - Referências existentes
        """

        for node in self.nodes.values():

            if not node.validate():

                return False



        for edge in self.edges.values():

            if not edge.validate():

                return False



            if edge.source_id not in self.nodes:

                return False



            if edge.target_id not in self.nodes:

                return False



        for path in self.paths.values():

            if not path.validate():

                return False


            for node_id in path.nodes:

                if node_id not in self.nodes:

                    return False



            for edge_id in path.edges:

                if edge_id not in self.edges:

                    return False



        return True



    # ==========================================================
    # 21. ESTATÍSTICAS DO GRAFO
    # ==========================================================

    def stats(
        self
    ) -> Dict[str, Any]:
        """
        Retorna métricas estruturais
        do conhecimento armazenado.
        """

        evidence_count = len(
            self.list_evidences()
        )


        validated_nodes = 0


        for node in self.nodes.values():

            if getattr(
                node,
                "validation_status",
                None
            ) == "validated":

                validated_nodes += 1



        validation_ratio = 0.0


        if len(self.nodes) > 0:

            validation_ratio = (

                validated_nodes

                /

                len(self.nodes)

            )



        return {

            "graph_id":
                self.graph_id,


            "name":
                self.name,


            "nodes":
                len(self.nodes),


            "edges":
                len(self.edges),


            "paths":
                len(self.paths),


            "evidences":
                evidence_count,


            "validated_ratio":
                validation_ratio

        }



    # ==========================================================
    # 22. ADICIONAR METADADO DO GRAFO
    # ==========================================================

    def add_metadata(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Adiciona informação
        administrativa ao grafo.
        """

        self.metadata[key] = value



    # ==========================================================
    # 23. EXPORTAR KNOWLEDGE GRAPH
    # ==========================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:
        """
        Exporta o grafo completo
        para estrutura serializável.
        """

        return {

            "graph_id":
                self.graph_id,


            "name":
                self.name,


            "created_at":
                self.created_at,


            "metadata":
                self.metadata,


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

                ]

        }



    # ==========================================================
    # 24. LIMPAR GRAFO
    # ==========================================================

    def clear(
        self
    ) -> None:
        """
        Remove todo conteúdo
        do KnowledgeGraph.
        """

        self.nodes.clear()

        self.edges.clear()

        self.paths.clear()



    # ==========================================================
    # 25. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self
    ) -> str:

        stats = self.stats()


        return (

            f"KnowledgeGraph("
            f"id={stats['graph_id']}, "
            f"nodes={stats['nodes']}, "
            f"edges={stats['edges']}, "
            f"paths={stats['paths']}, "
            f"evidences={stats['evidences']}"
            f")"

        )