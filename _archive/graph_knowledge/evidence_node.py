from typing import (
    Any,
    Dict,
    Optional,
    List,
)

from _archive.graph_knowledge.knowledge_node import KnowledgeNode



class EvidenceNode(KnowledgeNode):
    """
    Representa uma evidência científica
    dentro do KALATRACE.

    EvidenceNode é uma especialização
    de KnowledgeNode.

    Responsabilidades:

    - armazenar dados da evidência;
    - registrar características metodológicas;
    - acompanhar maturidade científica;
    - fornecer base para validação epistemológica.

    Exemplos:

    - estudo in vitro;
    - estudo animal;
    - estudo observacional;
    - ensaio clínico;
    - revisão sistemática;
    - metanálise.
    """



    # ==========================================================
    # CONSTANTES DE VALIDAÇÃO
    # ==========================================================


    ALLOWED_RESEARCH_STAGES = [

        "discovery",

        "preclinical",

        "clinical_phase_1",

        "clinical_phase_2",

        "clinical_phase_3",

        "approved",

        "systematic_review",

    ]



    ALLOWED_REPLICATION_STATUS = [

        "not_tested",

        "replicated",

        "failed_replication",

    ]



    ALLOWED_EVIDENCE_TYPES = [

        "in_vitro",

        "animal",

        "observational",

        "clinical_trial",

        "systematic_review",

        "meta_analysis",

        "case_report",

        "other",

    ]



    # ==========================================================
    # CONSTRUTOR
    # ==========================================================


    def __init__(
        self,
        node_id: str,
        title: str,
        evidence_type: str,
        research_stage: str,
        source: str = "unknown",
        confidence: float = 0.0,
        properties: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:
        """
        Inicializa uma evidência científica.
        """


        if not evidence_type:

            raise ValueError(
                "evidence_type cannot be empty."
            )


        if not research_stage:

            raise ValueError(
                "research_stage cannot be empty."
            )


        if research_stage not in self.ALLOWED_RESEARCH_STAGES:

            raise ValueError(
                f"Invalid research stage: {research_stage}"
            )


        super().__init__(
            node_id=node_id,
            node_type="Evidence",
            label=title,
            confidence=confidence,
            domain="scientific_evidence",
            source=source,
            properties=properties,
        )


        self.evidence_type = evidence_type


        self.research_stage = research_stage



        self.properties.setdefault(
            "replication_status",
            "not_tested"
        )


        self.properties.setdefault(
            "methodology",
            None
        )



    # ==========================================================
    # CONTROLE INTERNO DE ALTERAÇÃO
    # ==========================================================


    def _touch(
        self
    ) -> None:
        """
        Atualiza controle interno
        de versão do conhecimento.
        """


        self.version += 1


        from datetime import datetime, UTC


        self.updated_at = (
            datetime.now(
                UTC
            )
            .isoformat()
        )



    # ==========================================================
    # 1. DEFINIR ORGANISMO ESTUDADO
    # ==========================================================


    def set_organism(
        self,
        organism: str,
    ) -> None:
        """
        Define o organismo utilizado
        no estudo.
        """


        if not organism:

            raise ValueError(
                "organism cannot be empty."
            )


        self.properties[
            "organism"
        ] = organism


        self._touch()



    # ==========================================================
    # 2. DEFINIR MODELO EXPERIMENTAL
    # ==========================================================


    def set_model(
        self,
        model: str,
    ) -> None:
        """
        Define o modelo experimental.
        """


        if not model:

            raise ValueError(
                "model cannot be empty."
            )


        self.properties[
            "experimental_model"
        ] = model


        self._touch()



    # ==========================================================
    # 3. DEFINIR POPULAÇÃO DO ESTUDO
    # ==========================================================


    def set_population(
        self,
        population: Dict[str, Any],
    ) -> None:
        """
        Define população estudada.
        """


        if not isinstance(
            population,
            dict,
        ):

            raise TypeError(
                "population must be a dictionary."
            )


        self.properties[
            "study_population"
        ] = dict(
            population
        )


        self._touch()
    # ==========================================================
    # 4. DEFINIR FASE DA PESQUISA
    # ==========================================================


    def set_research_stage(
        self,
        stage: str,
    ) -> None:
        """
        Atualiza o estágio
        de desenvolvimento científico.
        """


        if stage not in self.ALLOWED_RESEARCH_STAGES:

            raise ValueError(
                f"Invalid research stage: {stage}"
            )


        self.research_stage = stage


        self._touch()



    # ==========================================================
    # 5. DEFINIR METODOLOGIA
    # ==========================================================


    def set_methodology(
        self,
        methodology: str,
    ) -> None:
        """
        Define o desenho metodológico
        utilizado pela evidência.

        Exemplos:

        - randomized_controlled_trial
        - observational_study
        - cohort_study
        - meta_analysis
        """


        if not methodology:

            raise ValueError(
                "methodology cannot be empty."
            )


        self.properties[
            "methodology"
        ] = methodology


        self._touch()



    # ==========================================================
    # 6. DEFINIR DESENHO DO ENSAIO
    # ==========================================================


    def set_trial_design(
        self,
        design: Dict[str, Any],
    ) -> None:
        """
        Define características
        experimentais do estudo.
        """


        if not isinstance(
            design,
            dict,
        ):

            raise TypeError(
                "design must be a dictionary."
            )


        self.properties[
            "trial_design"
        ] = dict(
            design
        )


        self._touch()



    # ==========================================================
    # 7. DEFINIR PUBLICAÇÃO
    # ==========================================================


    def set_publication(
        self,
        publication: Dict[str, Any],
    ) -> None:
        """
        Registra dados bibliográficos
        associados à evidência.
        """


        if not isinstance(
            publication,
            dict,
        ):

            raise TypeError(
                "publication must be a dictionary."
            )


        self.properties[
            "publication"
        ] = dict(
            publication
        )


        self._touch()



    # ==========================================================
    # 8. DEFINIR AUTORES
    # ==========================================================


    def set_authors(
        self,
        authors: List[str],
    ) -> None:
        """
        Registra autores
        responsáveis pelo estudo.
        """


        if not isinstance(
            authors,
            list,
        ):

            raise TypeError(
                "authors must be a list."
            )


        self.properties[
            "authors"
        ] = list(
            authors
        )


        self._touch()



    # ==========================================================
    # 9. DEFINIR LIMITAÇÕES
    # ==========================================================


    def set_limitations(
        self,
        limitations: List[str],
    ) -> None:
        """
        Registra limitações
        metodológicas da evidência.
        """


        if not isinstance(
            limitations,
            list,
        ):

            raise TypeError(
                "limitations must be a list."
            )


        self.properties[
            "limitations"
        ] = list(
            limitations
        )


        self._touch()



    # ==========================================================
    # 10. DEFINIR STATUS DE REPLICAÇÃO
    # ==========================================================


    def set_replication_status(
        self,
        status: str,
    ) -> None:
        """
        Define se o resultado
        foi replicado.
        """


        if status not in self.ALLOWED_REPLICATION_STATUS:

            raise ValueError(
                f"Invalid replication status: {status}"
            )


        self.properties[
            "replication_status"
        ] = status


        self._touch()



    # ==========================================================
    # 11. ADICIONAR RESULTADO PRINCIPAL
    # ==========================================================


    def set_main_finding(
        self,
        finding: str,
    ) -> None:
        """
        Registra o principal achado
        científico da evidência.
        """


        if not finding:

            raise ValueError(
                "finding cannot be empty."
            )


        self.properties[
            "main_finding"
        ] = finding


        self._touch()



    # ==========================================================
    # 12. ADICIONAR DOI / IDENTIFICADOR
    # ==========================================================


    def set_identifier(
        self,
        identifier_type: str,
        identifier_value: str,
    ) -> None:
        """
        Registra identificadores externos.

        Exemplos:

        DOI
        PMID
        ClinicalTrialID
        """


        if not identifier_type:

            raise ValueError(
                "identifier_type cannot be empty."
            )


        if not identifier_value:

            raise ValueError(
                "identifier_value cannot be empty."
            )


        identifiers = self.properties.setdefault(
            "identifiers",
            {}
        )


        identifiers[
            identifier_type
        ] = identifier_value


        self._touch()



    # ==========================================================
    # 13. CALCULAR MATURIDADE DA EVIDÊNCIA
    # ==========================================================


    def calculate_evidence_maturity(
        self,
    ) -> str:
        """
        Calcula maturidade epistemológica
        aproximada da evidência.

        Retorno:

        low
        moderate
        high
        """


        score = 0



        stage_scores = {

            "discovery": 1,

            "preclinical": 2,

            "clinical_phase_1": 3,

            "clinical_phase_2": 4,

            "clinical_phase_3": 5,

            "approved": 6,

            "systematic_review": 6,

        }


        score += stage_scores.get(
            self.research_stage,
            0,
        )



        methodology = self.properties.get(
            "methodology"
        )


        if methodology == (
            "randomized_controlled_trial"
        ):

            score += 2


        elif methodology:

            score += 1



        replication = self.properties.get(
            "replication_status"
        )


        if replication == "replicated":

            score += 2



        limitations = self.properties.get(
            "limitations",
            []
        )


        if len(limitations) > 3:

            score -= 1



        if score >= 8:

            return "high"



        if score >= 5:

            return "moderate"



        return "low"
    # ==========================================================
    # 14. OBTER RESUMO DA EVIDÊNCIA
    # ==========================================================


    def summary(
        self,
    ) -> Dict[str, Any]:
        """
        Retorna um resumo estruturado
        da evidência científica.
        """


        return {

            "id":
                self.node_id,


            "title":
                self.label,


            "type":
                self.evidence_type,


            "research_stage":
                self.research_stage,


            "maturity":
                self.calculate_evidence_maturity(),


            "confidence":
                self.confidence,


            "validation_status":
                self.validation_status,

        }



    # ==========================================================
    # 15. EXPORTAR EVIDÊNCIA
    # ==========================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Exporta EvidenceNode
        em formato serializável.

        Compatível com:

        - persistência;
        - auditoria;
        - APIs;
        - exportação JSON.
        """


        data = super().to_dict()



        data.update(
            {

                "evidence_type":
                    self.evidence_type,


                "research_stage":
                    self.research_stage,


                "evidence_maturity":
                    self.calculate_evidence_maturity(),

            }
        )



        return data



    # ==========================================================
    # 16. VALIDAR EVIDÊNCIA
    # ==========================================================


    def validate(
        self,
    ) -> bool:
        """
        Validação específica
        da evidência científica.
        """


        if not super().validate():

            return False



        if not self.evidence_type:

            return False



        if self.research_stage not in self.ALLOWED_RESEARCH_STAGES:

            return False



        if (
            self.confidence < 0
            or
            self.confidence > 1
        ):

            return False



        return True



    # ==========================================================
    # 17. COMPARAR EVIDÊNCIAS
    # ==========================================================


    def equals(
        self,
        other,
    ) -> bool:
        """
        Verifica se duas evidências
        representam a mesma entidade.
        """


        if not isinstance(
            other,
            EvidenceNode,
        ):

            return False



        return (
            self.node_id
            ==
            other.node_id
        )



    # ==========================================================
    # 18. REPRESENTAÇÃO
    # ==========================================================


    def __repr__(
        self,
    ) -> str:

        return (

            f"EvidenceNode("
            f"id={self.node_id}, "
            f"type={self.evidence_type}, "
            f"stage={self.research_stage}, "
            f"maturity="
            f"{self.calculate_evidence_maturity()}"
            f")"

        )