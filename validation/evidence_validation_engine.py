from __future__ import annotations


from datetime import (
    datetime,
    UTC,
)


from typing import (
    Any,
)


from contracts.iec_contract import IECContract
from contracts.evidence_contract import EvidenceContract
from storage.evidence_store import EvidenceStore



class EvidenceValidationEngine:
    """
    Motor responsável pela validação epistemológica
    dentro do KALATRACE.

    Responsabilidades:

    - analisar suporte de evidências;
    - avaliar força de sustentação;
    - identificar ausência de evidências;
    - gerar diagnóstico epistemológico.

    O EvidenceValidationEngine não determina
    verdade científica.

    Ele calcula níveis de sustentação
    com base nas evidências disponíveis.

    Migrado de core/validation_engine.py para validation/ (T1.4b,
    sessão de 03/08/2026). Renomeado de ValidationEngine para
    EvidenceValidationEngine para não colidir com
    validation.validation_engine.ValidationEngine (motor estrutural),
    que é uma responsabilidade genuinamente diferente -- não uma
    duplicata. Ver achado T0.5/T1.4a: este motor valida um IECContract
    isolado a partir de evidências, sem tocar o grafo; o motor
    estrutural valida o grafo inteiro e muta a confidence dos nós. Os
    dois continuam existindo lado a lado, por decisão.
    """


    def __init__(
        self,
        evidence_store: EvidenceStore,
    ) -> None:
        """
        Initializes the validation engine.
        """


        if not isinstance(
            evidence_store,
            EvidenceStore,
        ):
            raise TypeError(
                "evidence_store must be an EvidenceStore."
            )


        self.evidence_store = evidence_store


        # Histórico das validações realizadas.

        self.validation_history: list[
            dict[str, Any]
        ] = []



    # ==========================================================
    # REGISTRO INTERNO
    # ==========================================================

    def _register_event(
        self,
        event: str,
        details: dict[str, Any],
    ) -> None:
        """
        Registers an internal engine event.
        """


        self.validation_history.append(

            {

                "event":
                    event,

                "details":
                    details,

                "timestamp":
                    datetime.now(
                        UTC
                    ),

            }

        )



    # ==========================================================
    # 1. VALIDAR IEC
    # ==========================================================

    def validate_iec(
        self,
        iec: IECContract,
    ) -> dict[str, Any]:
        """
        Executa uma validação epistemológica
        inicial de uma IEC.

        Avalia:

        - integridade da IEC;
        - existência de evidências;
        - força média das evidências;
        - classificação inicial.
        """


        if not isinstance(
            iec,
            IECContract,
        ):
            raise TypeError(
                "iec must be an IECContract."
            )


        iec.validate()


        evidences = (
            self.evidence_store
            .get_evidence_for_iec(
                iec.iec_id
            )
        )


        evidence_count = len(
            evidences
        )


        strength = (
            self.evidence_store
            .compute_evidence_strength(
                iec.iec_id
            )
        )


        classification = (
            self._classify_strength(
                strength,
                evidence_count,
            )
        )


        result = {

            "iec_id":
                iec.iec_id,

            "statement":
                iec.statement,

            "evidence_count":
                evidence_count,

            "evidence_strength":
                strength,

            "classification":
                classification,

            "validated":
                True,

        }


        self._register_event(

            "iec_validated",

            result,

        )


        return result
    # ==========================================================
    # 2. CLASSIFICAÇÃO DA FORÇA
    # ==========================================================

    def _classify_strength(
        self,
        strength: float,
        evidence_count: int,
    ) -> str:
        """
        Classifica o nível atual de sustentação
        epistemológica.

        Não representa verdade absoluta.

        Representa apenas a força das
        evidências atualmente disponíveis.
        """


        if evidence_count == 0:
            return "INSUFFICIENT"


        if strength >= 0.75:
            return "STRONG"


        if strength >= 0.50:
            return "MODERATE"


        if strength >= 0.25:
            return "WEAK"


        return "INSUFFICIENT"



    # ==========================================================
    # 3. COMPARAR SUPORTE ENTRE IECs
    # ==========================================================

    def compare_iec_support(
        self,
        iec_a: IECContract,
        iec_b: IECContract,
    ) -> dict[str, Any]:
        """
        Compares the epistemic support
        of two IECs.

        The comparison considers only
        current evidence support.
        """


        if not isinstance(
            iec_a,
            IECContract,
        ):
            raise TypeError(
                "iec_a must be IECContract."
            )


        if not isinstance(
            iec_b,
            IECContract,
        ):
            raise TypeError(
                "iec_b must be IECContract."
            )


        strength_a = (
            self.evidence_store
            .compute_evidence_strength(
                iec_a.iec_id
            )
        )


        strength_b = (
            self.evidence_store
            .compute_evidence_strength(
                iec_b.iec_id
            )
        )


        difference = (
            strength_a -
            strength_b
        )


        if difference > 0:

            stronger = iec_a.iec_id


        elif difference < 0:

            stronger = iec_b.iec_id


        else:

            stronger = "EQUAL"



        result = {

            "iec_a":
                iec_a.iec_id,

            "iec_b":
                iec_b.iec_id,

            "support_difference":
                difference,

            "stronger_support":
                stronger,

        }


        self._register_event(

            "iec_support_compared",

            result,

        )


        return result



    # ==========================================================
    # 4. VALIDAR EVIDÊNCIA
    # ==========================================================

    def validate_evidence(
        self,
        evidence: EvidenceContract,
    ) -> dict[str, Any]:
        """
        Executes validation of an evidence object.

        Checks:

        - evidence integrity;
        - required structure;
        - availability of linked information.

        This method does not judge scientific truth.
        It only validates epistemological availability.
        """


        if not isinstance(
            evidence,
            EvidenceContract,
        ):
            raise TypeError(
                "evidence must be an EvidenceContract."
            )


        evidence.validate()


        result = {

            "evidence_id":
                evidence.evidence_id,

            "validated":
                True,

            "status":
                "AVAILABLE",

        }


        self._register_event(

            "evidence_validated",

            result,

        )


        return result
    # ==========================================================
    # 5. DIAGNÓSTICO EPISTEMOLÓGICO
    # ==========================================================

    def generate_diagnostic(
        self,
        iec: IECContract,
    ) -> dict[str, Any]:
        """
        Generates an epistemological diagnosis
        for an IEC.

        The diagnosis represents the current
        evidence state, not scientific truth.
        """


        validation = (
            self.validate_iec(
                iec
            )
        )


        diagnostic = {

            "iec_id":
                validation["iec_id"],

            "classification":
                validation["classification"],

            "evidence_strength":
                validation["evidence_strength"],

            "evidence_count":
                validation["evidence_count"],

            "interpretation":
                self._interpret_strength(
                    validation["classification"]
                ),

        }


        self._register_event(

            "diagnostic_generated",

            diagnostic,

        )


        return diagnostic



    # ==========================================================
    # 6. INTERPRETAÇÃO DE FORÇA EPISTEMOLÓGICA
    # ==========================================================

    def _interpret_strength(
        self,
        classification: str,
    ) -> str:
        """
        Converts the internal classification
        into an epistemological interpretation.

        This is descriptive only.

        It does not represent truth evaluation.
        """


        interpretations = {

            "STRONG":
                (
                    "Strong epistemological support "
                    "based on currently available evidence."
                ),


            "MODERATE":
                (
                    "Moderate support. "
                    "Additional evidence may strengthen "
                    "or challenge the current understanding."
                ),


            "WEAK":
                (
                    "Weak support. "
                    "Evidence exists but remains limited."
                ),


            "INSUFFICIENT":
                (
                    "Insufficient evidence available "
                    "for meaningful support evaluation."
                ),

        }


        return interpretations.get(

            classification,

            "Unknown epistemological state.",

        )



    # ==========================================================
    # 7. ANÁLISE DE LACUNAS DE EVIDÊNCIA
    # ==========================================================

    def analyze_evidence_gaps(
        self,
        iec: IECContract,
    ) -> dict[str, Any]:
        """
        Identifies possible evidence gaps
        related to an IEC.

        The method highlights missing support
        conditions without determining validity.
        """


        if not isinstance(
            iec,
            IECContract,
        ):
            raise TypeError(
                "iec must be an IECContract."
            )


        evidences = (
            self.evidence_store
            .get_evidence_for_iec(
                iec.iec_id
            )
        )


        evidence_count = len(
            evidences
        )


        strength = (
            self.evidence_store
            .compute_evidence_strength(
                iec.iec_id
            )
        )


        gaps = []


        if evidence_count == 0:

            gaps.append(
                "No evidence associated with IEC."
            )


        if strength < 0.50:

            gaps.append(
                "Evidence strength below moderate threshold."
            )


        if evidence_count < 3:

            gaps.append(
                "Limited evidence diversity."
            )


        result = {

            "iec_id":
                iec.iec_id,

            "evidence_count":
                evidence_count,

            "evidence_strength":
                strength,

            "identified_gaps":
                gaps,

            "has_gaps":
                len(gaps) > 0,

        }


        self._register_event(

            "evidence_gap_analysis_completed",

            result,

        )


        return result
    # ==========================================================
    # 8. RANKING DE SUPORTE ENTRE IECs
    # ==========================================================

    def rank_iec_support(
        self,
        iecs: list[IECContract],
    ) -> list[dict[str, Any]]:
        """
        Ranks IECs according to their current
        evidence support.

        Ranking is based only on evidence strength.
        """


        if not isinstance(
            iecs,
            list,
        ):
            raise TypeError(
                "iecs must be a list."
            )


        ranking = []


        for iec in iecs:

            if not isinstance(
                iec,
                IECContract,
            ):
                raise TypeError(
                    "All items must be IECContract."
                )


            strength = (
                self.evidence_store
                .compute_evidence_strength(
                    iec.iec_id
                )
            )


            ranking.append(

                {

                    "iec_id":
                        iec.iec_id,

                    "statement":
                        iec.statement,

                    "evidence_strength":
                        strength,

                }

            )


        ranking.sort(

            key=lambda item:
                item["evidence_strength"],

            reverse=True,

        )


        self._register_event(

            "iec_support_ranking_generated",

            {

                "iec_count":
                    len(ranking),

            },

        )


        return ranking



    # ==========================================================
    # 9. HISTÓRICO DE VALIDAÇÕES
    # ==========================================================

    def get_validation_history(
        self,
    ) -> list[dict[str, Any]]:
        """
        Returns the internal validation history.

        The returned object is a copy,
        preventing direct mutation.
        """


        return list(
            self.validation_history
        )



    # ==========================================================
    # 10. LIMPEZA CONTROLADA DO HISTÓRICO
    # ==========================================================

    def clear_history(
        self,
    ) -> None:
        """
        Clears internal validation history.

        This operation only affects runtime
        memory and does not remove persisted data.
        """


        self.validation_history.clear()



    # ==========================================================
    # 11. ESTATÍSTICAS DO MOTOR
    # ==========================================================

    def stats(
        self,
    ) -> dict[str, Any]:
        """
        Returns operational metrics
        for the ValidationEngine.
        """


        return {

            "validation_events":
                len(
                    self.validation_history
                ),

            "engine":
                "ValidationEngine",

            "status":
                "active",

            "capabilities":
                [

                    "iec_validation",

                    "evidence_validation",

                    "epistemological_diagnosis",

                    "evidence_gap_analysis",

                    "support_ranking",

                ],

        }