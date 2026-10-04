from typing import (
    Any,
    Dict,
    Optional,
)

from datetime import (
    datetime,
    UTC,
)

from graph.base.edge import Edge



class KnowledgeEdge(Edge):
    """
    Especialização de Edge para representar
    relações epistemológicas e científicas
    dentro do KALATRACE.

    Exemplos:

    SUPPORTED_BY
    CONTRADICTS
    DERIVED_FROM
    EXPLAINS
    CAUSES
    CORRELATES_WITH
    ACTIVATES
    """


    ALLOWED_RELATION_TYPES = [

        "SUPPORTED_BY",

        "CONTRADICTS",

        "DERIVED_FROM",

        "EXPLAINS",

        "CAUSES",

        "CORRELATES_WITH",

        "ACTIVATES",

        "INHIBITS",

        "ASSOCIATED_WITH",

        "VALIDATED_BY",

        "RELATED_TO",

    ]



    ALLOWED_EVIDENCE_LEVELS = [

        "unknown",

        "theoretical",

        "computational",

        "preclinical",

        "clinical",

        "systematic_review",

        "meta_analysis",

        "guideline",

        "consensus",

    ]



    ALLOWED_VALIDATION_STATUS = [

        "pending",

        "under_review",

        "supported",

        "validated",

        "contradicted",

        "deprecated",

    ]



    def __init__(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        relation_type: str,
        confidence: float = 0.0,
        evidence_level: str = "unknown",
        properties: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Inicializa uma relação científica.
        """


        if not relation_type:

            raise ValueError(
                "relation_type cannot be empty."
            )


        if confidence < 0 or confidence > 1:

            raise ValueError(
                "Confidence must be between 0 and 1."
            )


        if evidence_level not in self.ALLOWED_EVIDENCE_LEVELS:

            raise ValueError(
                f"Invalid evidence level: {evidence_level}"
            )


        super().__init__(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties,
        )


        self.confidence = float(
            confidence
        )


        self.evidence_level = evidence_level


        self.validation_status = "pending"


        self.version = 1


        self.updated_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )
    # ==========================================================
    # CONTROLE INTERNO DE ALTERAÇÃO
    # ==========================================================


    def _touch(
        self
    ) -> None:
        """
        Atualiza controle interno
        de versão e modificação.
        """


        self.version += 1


        self.updated_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )



    # ==========================================================
    # 1. ATUALIZAR CONFIANÇA DA RELAÇÃO
    # ==========================================================


    def update_confidence(
        self,
        confidence: float,
    ) -> None:
        """
        Atualiza a força epistemológica
        da relação.
        """


        if confidence < 0.0 or confidence > 1.0:

            raise ValueError(
                "Confidence must be between 0 and 1."
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
        status: str,
    ) -> None:
        """
        Atualiza o estado epistemológico
        da relação.
        """


        if status not in self.ALLOWED_VALIDATION_STATUS:

            raise ValueError(
                f"Invalid validation status: {status}"
            )


        self.validation_status = status


        self._touch()



    # ==========================================================
    # 3. ATUALIZAR NÍVEL DE EVIDÊNCIA
    # ==========================================================


    def update_evidence_level(
        self,
        level: str,
    ) -> None:
        """
        Atualiza o nível científico
        associado à relação.
        """


        if level not in self.ALLOWED_EVIDENCE_LEVELS:

            raise ValueError(
                f"Invalid evidence level: {level}"
            )


        self.evidence_level = level


        self._touch()



    # ==========================================================
    # 4. ADICIONAR PROPRIEDADE
    # ==========================================================


    def add_property(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Adiciona metadados científicos
        à relação.

        Exemplos:

        - mecanismo associado;
        - contexto biológico;
        - observações;
        - condições.
        """


        if not key:

            raise ValueError(
                "Property key cannot be empty."
            )


        self.properties[key] = value


        self._touch()



    # ==========================================================
    # 5. OBTER PROPRIEDADE
    # ==========================================================


    def get_property(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Recupera uma propriedade
        da relação.
        """


        return self.properties.get(
            key,
            default,
        )



    # ==========================================================
    # 6. REMOVER PROPRIEDADE
    # ==========================================================


    def remove_property(
        self,
        key: str,
    ) -> bool:
        """
        Remove uma propriedade.
        """


        if key in self.properties:

            del self.properties[key]

            self._touch()

            return True


        return False



    # ==========================================================
    # 7. DEFINIR CONTEXTO CIENTÍFICO
    # ==========================================================


    def set_context(
        self,
        context: str,
    ) -> None:
        """
        Define o contexto científico
        onde a relação é válida.

        Exemplos:

        skin_regeneration

        oncology

        neurodegeneration
        """


        if not context:

            raise ValueError(
                "context cannot be empty."
            )


        self.properties[
            "context"
        ] = context


        self._touch()



    # ==========================================================
    # 8. DEFINIR MECANISMO RELACIONADO
    # ==========================================================


    def set_mechanism(
        self,
        mechanism: str,
    ) -> None:
        """
        Registra mecanismo biológico
        associado à relação.
        """


        if not mechanism:

            raise ValueError(
                "mechanism cannot be empty."
            )


        self.properties[
            "mechanism"
        ] = mechanism


        self._touch()
    # ==========================================================
    # 9. EXPORTAR KNOWLEDGE EDGE
    # ==========================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Converte a relação científica
        para formato serializável.

        Usado por:

        - persistência;
        - auditoria;
        - APIs;
        - exportação JSON.
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


            "confidence":
                self.confidence,


            "evidence_level":
                self.evidence_level,


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
    # 10. VALIDAR RELAÇÃO
    # ==========================================================


    def validate(
        self,
    ) -> bool:
        """
        Validação estrutural
        da relação epistemológica.
        """


        if not super().validate():

            return False



        if not self.relation_type:

            return False



        if (
            self.confidence < 0
            or
            self.confidence > 1
        ):

            return False



        if (
            self.evidence_level
            not in
            self.ALLOWED_EVIDENCE_LEVELS
        ):

            return False



        if (
            self.validation_status
            not in
            self.ALLOWED_VALIDATION_STATUS
        ):

            return False



        return True



    # ==========================================================
    # 11. VERIFICAR FORÇA DA RELAÇÃO
    # ==========================================================


    def is_strong(
        self,
        threshold: float = 0.7,
    ) -> bool:
        """
        Verifica se a relação possui
        alta confiança epistemológica.
        """


        return (
            self.confidence
            >=
            threshold
        )



    # ==========================================================
    # 12. COMPARAR RELAÇÕES
    # ==========================================================


    def equals(
        self,
        other,
    ) -> bool:
        """
        Verifica se duas relações
        representam a mesma entidade.
        """


        if not isinstance(
            other,
            KnowledgeEdge,
        ):

            return False



        return (
            self.edge_id
            ==
            other.edge_id
        )



    # ==========================================================
    # 13. REPRESENTAÇÃO
    # ==========================================================


    def __repr__(
        self,
    ) -> str:

        return (

            f"KnowledgeEdge("
            f"id={self.edge_id}, "
            f"relation={self.relation_type}, "
            f"confidence={self.confidence}, "
            f"evidence={self.evidence_level}, "
            f"status={self.validation_status}"
            f")"

        )