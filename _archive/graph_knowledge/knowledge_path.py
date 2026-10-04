from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from graph.base.path import Path


class KnowledgePath(Path):
    """
    Especialização de Path para representar
    caminhos de conhecimento científico
    dentro do KALATRACE.

    Representa cadeias epistemológicas:

    IEC
        |
        ↓
    Evidence
        |
        ↓
    Publication


    Ou:

    Mechanism
        |
        ↓
    Hypothesis
        |
        ↓
    Evidence
    """


    ALLOWED_VALIDATION_STATUS = [

        "pending",

        "under_review",

        "supported",

        "validated",

        "contradicted",

        "deprecated"

    ]


    ALLOWED_PATH_TYPES = [

        "knowledge_chain",

        "causal_chain",

        "evidence_chain",

        "mechanistic_path",

        "discovery_path",

        "contradiction_path"

    ]



    def __init__(
        self,
        path_id: str,
        nodes: List[str],
        edges: List[str],
        path_type: str = "knowledge_chain",
        confidence: float = 0.0,
        properties: Optional[
            Dict[str, Any]
        ] = None
    ):
        """
        Inicializa um caminho
        epistemológico.
        """


        super().__init__(
            path_id=path_id,
            nodes=nodes,
            edges=edges
        )


        if confidence < 0.0 or confidence > 1.0:

            raise ValueError(
                "confidence must be between 0 and 1"
            )


        self.path_type = path_type


        self.confidence = float(
            confidence
        )


        self.properties = (
            properties
            if properties is not None
            else {}
        )


        self.validation_status = (
            "pending"
        )


        self.version = 1


        self.updated_at = (
            datetime.now(UTC)
            .isoformat()
        )
    # ==========================================================
    # MÉTODO INTERNO DE ATUALIZAÇÃO
    # ==========================================================

    def _touch(
        self
    ) -> None:
        """
        Atualiza controle de versão
        e timestamp.
        """

        self.version += 1

        self.updated_at = (
            datetime.now(UTC)
            .isoformat()
        )



    # ==========================================================
    # 1. ATUALIZAR CONFIANÇA DO CAMINHO
    # ==========================================================

    def update_confidence(
        self,
        confidence: float
    ) -> None:
        """
        Atualiza a força epistemológica
        do caminho.
        """

        if confidence < 0.0 or confidence > 1.0:

            raise ValueError(
                "Confidence deve estar entre 0 e 1"
            )


        self.confidence = float(
            confidence
        )


        self._touch()



    # ==========================================================
    # 2. ATUALIZAR STATUS DE VALIDAÇÃO
    # ==========================================================

    def update_validation_status(
        self,
        status: str
    ) -> None:
        """
        Atualiza o estado epistemológico
        da cadeia de conhecimento.
        """

        if status not in self.ALLOWED_VALIDATION_STATUS:

            raise ValueError(
                f"Status inválido: {status}"
            )


        self.validation_status = status


        self._touch()



    # ==========================================================
    # 3. DEFINIR TIPO DO CAMINHO
    # ==========================================================

    def set_reasoning_type(
        self,
        reasoning_type: str
    ) -> None:
        """
        Define a natureza da cadeia
        de conhecimento.

        Exemplos:

        causal_chain

        evidence_chain

        mechanistic_path

        discovery_path

        contradiction_path
        """

        if reasoning_type not in self.ALLOWED_PATH_TYPES:

            raise ValueError(
                f"Tipo de caminho inválido: {reasoning_type}"
            )


        self.path_type = reasoning_type


        self._touch()



    # ==========================================================
    # 4. ADICIONAR PROPRIEDADE
    # ==========================================================

    def add_property(
        self,
        key: str,
        value: Any
    ) -> None:
        """
        Adiciona metadados ao caminho.

        Exemplos:

        - hipótese relacionada
        - domínio científico
        - contexto experimental
        - estratégia de busca
        """

        self.properties[key] = value


        self._touch()



    # ==========================================================
    # 5. OBTER PROPRIEDADE
    # ==========================================================

    def get_property(
        self,
        key: str,
        default=None
    ) -> Any:
        """
        Recupera uma propriedade
        específica.
        """

        return self.properties.get(
            key,
            default
        )



    # ==========================================================
    # 6. ADICIONAR NODE AO CAMINHO
    # ==========================================================

    def add_node(
        self,
        node_id: str
    ) -> None:
        """
        Adiciona um novo nó
        ao caminho epistemológico.
        """

        if not node_id:

            raise ValueError(
                "node_id cannot be empty"
            )


        self.nodes.append(
            node_id
        )


        self._touch()



    # ==========================================================
    # 7. ADICIONAR EDGE AO CAMINHO
    # ==========================================================

    def add_edge(
        self,
        edge_id: str
    ) -> None:
        """
        Adiciona uma relação
        ao caminho.
        """

        if not edge_id:

            raise ValueError(
                "edge_id cannot be empty"
            )


        self.edges.append(
            edge_id
        )


        self._touch()
    # ==========================================================
    # 8. VERIFICAR NODE NO CAMINHO
    # ==========================================================

    def contains_node(
        self,
        node_id: str
    ) -> bool:
        """
        Verifica se um Node pertence
        ao caminho.
        """

        return node_id in self.nodes



    # ==========================================================
    # 9. VERIFICAR EDGE NO CAMINHO
    # ==========================================================

    def contains_edge(
        self,
        edge_id: str
    ) -> bool:
        """
        Verifica se uma relação
        pertence ao caminho.
        """

        return edge_id in self.edges



    # ==========================================================
    # 10. CALCULAR COMPLEXIDADE
    # ==========================================================

    def complexity(
        self
    ) -> Dict[str, int]:
        """
        Retorna métricas estruturais
        do caminho.
        """

        return {

            "nodes":
                len(self.nodes),


            "edges":
                len(self.edges),


            "steps":
                len(self.edges)

        }



    # ==========================================================
    # 11. EXPORTAR KNOWLEDGE PATH
    # ==========================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:
        """
        Converte o caminho para
        formato serializável.
        """

        return {

            "path_id":
                self.path_id,


            "nodes":
                self.nodes,


            "edges":
                self.edges,


            "path_type":
                self.path_type,


            "confidence":
                self.confidence,


            "validation_status":
                self.validation_status,


            "version":
                self.version,


            "properties":
                self.properties,


            "updated_at":
                self.updated_at

        }



    # ==========================================================
    # 12. VALIDAR CAMINHO
    # ==========================================================

    def validate(
        self
    ) -> bool:
        """
        Valida integridade mínima
        do caminho epistemológico.
        """

        if not self.path_id:

            return False



        if len(self.nodes) < 2:

            return False



        if self.path_type not in self.ALLOWED_PATH_TYPES:

            return False



        if (
            self.confidence < 0
            or
            self.confidence > 1
        ):

            return False



        if self.validation_status not in self.ALLOWED_VALIDATION_STATUS:

            return False



        return True



    # ==========================================================
    # 13. COMPARAR PATHS
    # ==========================================================

    def equals(
        self,
        other
    ) -> bool:
        """
        Verifica se dois caminhos
        possuem o mesmo identificador.
        """

        if not isinstance(
            other,
            KnowledgePath
        ):

            return False


        return (

            self.path_id
            ==
            other.path_id

        )



    # ==========================================================
    # 14. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self
    ) -> str:

        return (

            f"KnowledgePath("
            f"id={self.path_id}, "
            f"type={self.path_type}, "
            f"nodes={len(self.nodes)}, "
            f"edges={len(self.edges)}, "
            f"confidence={self.confidence}, "
            f"status={self.validation_status}"
            f")"

        )