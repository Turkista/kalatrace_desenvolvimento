from __future__ import annotations

from datetime import (
    datetime,
    UTC,
)

from typing import (
    Any,
)


class ValidationEngine:
    """
    Motor de validação estrutural epistemológica
    do KALATRACE.

    Responsável por analisar:

    - consistência estrutural do grafo;
    - qualidade global do conhecimento;
    - força relativa dos IECs;
    - conflitos entre relações.

    Este componente não determina verdade científica.

    A validação científica baseada em evidências
    pertence ao validation.evidence_validation_engine
    (EvidenceValidationEngine — movido de core/validation_engine.py
    em T1.4b, sessão de 03/08/2026; ver achado T0.5/T1.4a: são
    responsabilidades diferentes, mantidas lado a lado por decisão,
    não fundidas).

    Este motor atua sobre a estrutura cognitiva
    representada no grafo.
    """


    def __init__(
        self,
        graph,
        evidence_store,
    ) -> None:
        """
        Initializes structural validation engine.
        """


        if graph is None:
            raise ValueError(
                "graph cannot be None."
            )


        if evidence_store is None:
            raise ValueError(
                "evidence_store cannot be None."
            )


        self.graph = graph

        self.evidence_store = evidence_store


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
        Registers validation activity.
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
    # 1. VALIDAR IEC INDIVIDUAL
    # ==========================================================

    def validate_iec(
        self,
        iec_id: str,
    ) -> dict[str, Any] | None:
        """
        Recalculates IEC confidence
        using available evidence strength.

        This operation evaluates structural
        confidence only.
        """


        iec = (
            self.graph
            .get_node(
                iec_id
            )
        )


        if not iec:
            return None


        old_confidence = (
            iec.confidence
        )


        evidence_strength = (

            self.evidence_store
            .compute_evidence_strength(
                iec_id
            )

        )


        new_confidence = (

            old_confidence
            +
            evidence_strength

        ) / 2


        iec.update_confidence(
            new_confidence
        )


        result = {

            "iec_id":
                iec_id,

            "old_confidence":
                old_confidence,

            "evidence_strength":
                evidence_strength,

            "new_confidence":
                new_confidence,

        }


        self._register_event(

            "iec_structural_validation",

            result,

        )


        return result
    # ==========================================================
    # 2. VALIDAR TODO O SISTEMA
    # ==========================================================

    def validate_all(
        self,
    ) -> list[dict[str, Any]]:
        """
        Revalidates all nodes available
        in the knowledge graph.

        Returns only successful validations.
        """


        results = []


        for iec_id in self.graph.nodes:


            result = (
                self.validate_iec(
                    iec_id
                )
            )


            if result:

                results.append(
                    result
                )


        self._register_event(

            "full_graph_validation_completed",

            {

                "validated_nodes":
                    len(results),

            },

        )


        return results



    # ==========================================================
    # 3. DETECTAR CONHECIMENTO FRACO
    # ==========================================================

    def weak_knowledge(
        self,
        threshold: float = 0.3,
    ) -> list[Any]:
        """
        Returns IEC nodes with confidence
        below the configured threshold.

        This identifies weak support,
        not incorrect knowledge.
        """


        weak = []


        for iec_id, iec in (
            self.graph.nodes.items()
        ):


            if (
                iec.confidence
                <
                threshold
            ):

                weak.append(
                    iec
                )


        self._register_event(

            "weak_knowledge_analysis",

            {

                "threshold":
                    threshold,

                "weak_count":
                    len(weak),

            },

        )


        return weak



    # ==========================================================
    # 4. DETECTAR CONTRADIÇÕES ESTRUTURAIS
    # ==========================================================

    def detect_basic_conflicts(
        self,
    ) -> list[dict[str, Any]]:
        """
        Detects basic structural conflicts
        inside graph relations.

        This does not perform semantic
        contradiction reasoning.
        """


        conflicts = []


        supports = set()

        contradictions = set()


        for edge in self.graph.edges:


            relation = (

                edge.get(
                    "type"
                )

            )


            pair = (

                edge.get(
                    "source"
                ),

                edge.get(
                    "target"
                ),

            )


            if relation == "supports":

                supports.add(
                    pair
                )


            elif relation == "contradicts":

                contradictions.add(
                    pair
                )



        for pair in (
            supports.intersection(
                contradictions
            )
        ):


            conflicts.append(

                {

                    "source":
                        pair[0],

                    "target":
                        pair[1],

                    "issue":
                        "support_vs_contradiction",

                }

            )


        self._register_event(

            "structural_conflict_detection",

            {

                "conflicts_found":
                    len(conflicts),

            },

        )


        return conflicts
    # ==========================================================
    # 5. SCORE GLOBAL DO SISTEMA
    # ==========================================================

    def system_quality_score(
        self,
    ) -> float:
        """
        Calculates a structural quality score
        for the knowledge graph.

        The score considers:

        - average IEC confidence;
        - isolated node penalty.

        It does not represent scientific truth.
        """


        nodes = list(
            self.graph.nodes.values()
        )


        if not nodes:
            return 0.0



        avg_confidence = (

            sum(
                node.confidence
                for node in nodes
            )

            /
            len(nodes)

        )


        isolated_nodes = (
            self.graph
            .isolated_nodes()
        )


        isolated_penalty = (

            len(
                isolated_nodes
            )

            *
            0.01

        )


        score = max(

            0.0,

            avg_confidence
            -
            isolated_penalty,

        )


        self._register_event(

            "system_quality_score_calculated",

            {

                "score":
                    score,

                "nodes":
                    len(nodes),

                "isolated_nodes":
                    len(isolated_nodes),

            },

        )


        return score



    # ==========================================================
    # 6. RELATÓRIO GERAL
    # ==========================================================

    def report(
        self,
    ) -> dict[str, Any]:
        """
        Generates structural health report
        of the knowledge graph.
        """


        report = {

            "system_score":
                self.system_quality_score(),

            "weak_knowledge":
                len(
                    self.weak_knowledge()
                ),

            "conflicts":
                len(
                    self.detect_basic_conflicts()
                ),

            "total_nodes":
                len(
                    self.graph.nodes
                ),

            "total_edges":
                len(
                    self.graph.edges
                ),

        }


        self._register_event(

            "validation_report_generated",

            report,

        )


        return report



    # ==========================================================
    # 7. HISTÓRICO DE VALIDAÇÃO
    # ==========================================================

    def get_validation_history(
        self,
    ) -> list[dict[str, Any]]:
        """
        Returns validation activity history.
        """


        return list(
            self.validation_history
        )



    # ==========================================================
    # 8. ESTATÍSTICAS DO MOTOR
    # ==========================================================

    def stats(
        self,
    ) -> dict[str, Any]:
        """
        Returns operational metrics.
        """


        return {

            "engine":
                "StructuralValidationEngine",

            "events":
                len(
                    self.validation_history
                ),

            "status":
                "active",

            "capabilities":
                [

                    "iec_structural_validation",

                    "weak_knowledge_detection",

                    "graph_conflict_detection",

                    "system_quality_analysis",

                ],

        }