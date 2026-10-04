from __future__ import annotations


from datetime import (
    datetime,
    UTC,
)


from typing import (
    Any,
)


from utils.embeddings import cosine_similarity
from governance.rules import MIN_EDGE_WEIGHT



class Evaluator:
    """
    Avaliador epistemológico do KALATRACE.

    Responsável por analisar a qualidade
    das conexões do grafo.

    O Evaluator não altera a verdade
    dos elementos do conhecimento.

    Ele apenas calcula qualidade estrutural
    das relações existentes.
    """


    def __init__(
        self,
    ) -> None:
        """
        Initializes evaluator state.
        """


        self.evaluation_history: list[
            dict[str, Any]
        ] = []



    # ======================================================
    # REGISTRO INTERNO
    # ======================================================

    def _register_event(
        self,
        event: str,
        details: dict[str, Any],
    ) -> None:
        """
        Registers governance evaluation events.
        """


        self.evaluation_history.append(

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



    # ======================================================
    # AVALIAÇÃO DE ARESTA
    # ======================================================

    def evaluate_edge(
        self,
        edge: dict[str, Any],
        graph,
    ) -> float:
        """
        Evaluates epistemological quality
        of a graph edge.

        Score:

        embedding_similarity *
        edge_weight
        """


        if not isinstance(
            edge,
            dict,
        ):
            raise TypeError(
                "edge must be a dictionary."
            )


        if "source" not in edge:
            raise ValueError(
                "edge requires source."
            )


        if "target" not in edge:
            raise ValueError(
                "edge requires target."
            )


        if "weight" not in edge:
            raise ValueError(
                "edge requires weight."
            )


        source = graph.get_node(
            edge["source"]
        )


        target = graph.get_node(
            edge["target"]
        )


        if source is None or target is None:
            return 0.0


        if not hasattr(
            source,
            "embedding",
        ):
            return 0.0


        if not hasattr(
            target,
            "embedding",
        ):
            return 0.0


        similarity = cosine_similarity(
            source.embedding,
            target.embedding,
        )


        score = (
            similarity *
            float(edge["weight"])
        )


        self._register_event(

            "edge_evaluated",

            {

                "source":
                    edge["source"],

                "target":
                    edge["target"],

                "score":
                    score,

            },

        )


        return score
    # ======================================================
    # FILTRAGEM DE ARESTAS
    # ======================================================

    def filter_edges(
        self,
        graph,
        min_score: float = MIN_EDGE_WEIGHT,
    ):
        """
        Filters graph edges according to
        epistemological quality threshold.

        The method preserves the original
        graph object to maintain compatibility
        with existing architecture.
        """


        if not isinstance(
            min_score,
            (float, int),
        ):
            raise TypeError(
                "min_score must be numeric."
            )


        valid_edges = []

        rejected_edges = []


        for edge in graph.edges:


            score = self.evaluate_edge(
                edge,
                graph,
            )


            if score >= min_score:

                edge["quality_score"] = score

                valid_edges.append(
                    edge
                )


            else:

                rejected_edges.append(

                    {

                        "edge":
                            edge,

                        "quality_score":
                            score,

                    }

                )



        # Mantém comportamento original:
        # o grafo continua sendo atualizado.

        graph.edges = valid_edges



        result = {

            "accepted_edges":
                len(valid_edges),

            "rejected_edges":
                len(rejected_edges),

            "minimum_score":
                min_score,

        }


        self._register_event(

            "edge_filter_completed",

            result,

        )


        return graph



    # ======================================================
    # RELATÓRIO DE GOVERNANÇA
    # ======================================================

    def governance_report(
        self,
    ) -> dict[str, Any]:
        """
        Returns governance evaluation metrics.
        """


        return {

            "evaluator":
                "Evaluator",

            "evaluation_events":
                len(
                    self.evaluation_history
                ),

            "status":
                "active",

        }



    # ======================================================
    # HISTÓRICO
    # ======================================================

    def get_history(
        self,
    ) -> list[dict[str, Any]]:
        """
        Returns evaluation history.

        The returned object is a copy
        to avoid external mutation.
        """


        return list(
            self.evaluation_history
        )