from datetime import datetime, UTC
from typing import Any, Dict, Optional

from graph.base.node import Node


class KnowledgeNode(Node):
    """
    Especialização de Node para representar
    unidades de conhecimento científico
    dentro do KALATRACE.

    Exemplos:

    - IEC
    - Evidence
    - Hypothesis
    - Concept
    - Mechanism
    - Scientific Finding


    Responsabilidade:

    Apenas representar conhecimento.

    Regras epistemológicas complexas
    pertencem aos Engines superiores.
    """


    ALLOWED_STATUSES = [

        "pending",

        "under_review",

        "supported",

        "validated",

        "contradicted",

        "deprecated"

    ]


    def __init__(
        self,
        node_id: str,
        node_type: str,
        label: str,
        confidence: float = 0.0,
        domain: str = "general",
        source: str = "unknown",
        properties: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Inicializa um KnowledgeNode.
        """


        if confidence < 0.0 or confidence > 1.0:

            raise ValueError(
                "confidence must be between 0 and 1."
            )


        super().__init__(
            node_id=node_id,
            node_type=node_type,
            label=label,
            properties=properties,
        )


        self.confidence = float(
            confidence
        )


        self.domain = domain


        self.source = source


        self.validation_status = (
            "pending"
        )


        self.version = 1


        self.updated_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )



    # ==========================================================
    # INTERNAL UPDATE CONTROL
    # ==========================================================

    def _touch(
        self
    ) -> None:
        """
        Atualiza controle interno
        de versão e tempo.
        """


        self.version += 1


        self.updated_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )
    # ==========================================================
    # 1. ATUALIZAR CONFIANÇA
    # ==========================================================

    def update_confidence(
        self,
        confidence: float,
    ) -> None:
        """
        Atualiza o nível de confiança
        do conhecimento.
        """


        if confidence < 0.0 or confidence > 1.0:

            raise ValueError(
                "confidence must be between 0 and 1."
            )


        self.confidence = float(
            confidence
        )


        self._touch()



    # ==========================================================
    # 2. ALTERAR STATUS DE VALIDAÇÃO
    # ==========================================================

    def update_validation_status(
        self,
        status: str,
    ) -> None:
        """
        Atualiza o estado epistemológico
        do conhecimento.
        """


        if status not in self.ALLOWED_STATUSES:

            raise ValueError(
                f"Invalid validation status: {status}"
            )


        self.validation_status = status


        self._touch()



    # ==========================================================
    # 3. ADICIONAR PROPRIEDADE CIENTÍFICA
    # ==========================================================

    def add_property(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Adiciona uma propriedade
        científica ao conhecimento.

        Mantém controle de versão.
        """


        super().add_property(
            key,
            value,
        )


        self._touch()



    # ==========================================================
    # 4. OBTER PROPRIEDADE
    # ==========================================================

    def get_property(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Recupera uma propriedade
        científica.
        """


        return self.properties.get(
            key,
            default,
        )



    # ==========================================================
    # 5. ASSOCIAR EVIDÊNCIA
    # ==========================================================

    def add_evidence_reference(
        self,
        evidence_id: str,
    ) -> None:
        """
        Registra uma referência
        para uma evidência relacionada.
        """


        if not evidence_id:

            raise ValueError(
                "evidence_id cannot be empty."
            )


        evidences = self.properties.setdefault(
            "evidences",
            [],
        )


        if evidence_id not in evidences:

            evidences.append(
                evidence_id
            )

            self._touch()



    # ==========================================================
    # 6. LISTAR EVIDÊNCIAS
    # ==========================================================

    def get_evidence_references(
        self,
    ) -> list[str]:
        """
        Retorna IDs das evidências
        associadas.
        """


        return list(
            self.properties.get(
                "evidences",
                [],
            )
        )



    # ==========================================================
    # 7. VERIFICAR SE POSSUI EVIDÊNCIA
    # ==========================================================

    def has_evidence(
        self,
        evidence_id: str,
    ) -> bool:
        """
        Verifica se uma evidência
        está associada ao conhecimento.
        """


        return evidence_id in (
            self.properties.get(
                "evidences",
                [],
            )
        )
    # ==========================================================
    # 8. EXPORTAR KNOWLEDGE NODE
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Converte o KnowledgeNode
        para estrutura serializável.

        Usado por:

        - persistência;
        - APIs;
        - auditoria;
        - exportação científica.
        """


        return {

            "node_id":
                self.node_id,


            "node_type":
                self.node_type,


            "label":
                self.label,


            "confidence":
                self.confidence,


            "domain":
                self.domain,


            "source":
                self.source,


            "validation_status":
                self.validation_status,


            "version":
                self.version,


            "properties":
                dict(
                    self.properties
                ),


            "created_at":
                self.created_at,


            "updated_at":
                self.updated_at,

        }



    # ==========================================================
    # 9. VALIDAR CONHECIMENTO
    # ==========================================================

    def validate(
        self,
    ) -> bool:
        """
        Validação estrutural mínima
        do KnowledgeNode.
        
        Não executa validação científica.
        Isso pertence aos Validators
        e Engines superiores.
        """


        if not super().validate():

            return False



        if (
            self.confidence < 0.0
            or
            self.confidence > 1.0
        ):

            return False



        if (
            self.validation_status
            not in self.ALLOWED_STATUSES
        ):

            return False



        if not self.domain:

            return False



        return True



    # ==========================================================
    # 10. COMPARAR KNOWLEDGE NODES
    # ==========================================================

    def equals(
        self,
        other,
    ) -> bool:
        """
        Verifica se dois KnowledgeNodes
        representam a mesma entidade.
        """


        if not isinstance(
            other,
            KnowledgeNode,
        ):

            return False



        return (
            self.node_id
            ==
            other.node_id
        )



    # ==========================================================
    # 11. REPRESENTAÇÃO
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"KnowledgeNode("
            f"id={self.node_id}, "
            f"type={self.node_type}, "
            f"confidence={self.confidence}, "
            f"status={self.validation_status}"
            f")"

        )