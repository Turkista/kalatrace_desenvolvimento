from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from typing import (
    Any,
    Dict,
    List,
)

from contracts.iec_contract import (
    IECContract,
)

from storage.evidence_store import (
    EvidenceStore,
)



class EvidenceReasoningEngine:
    """
    Epistemological reasoning engine for KALATRACE.

    Responsible for:

    - analyzing IECs;
    - relating knowledge;
    - generating inferences;
    - discovering patterns;
    - suggesting future investigations.

    The EvidenceReasoningEngine never creates facts.

    It only derives conclusions from
    existing scientific knowledge.

    Migrado de core/reasoning_engine.py para engines/reasoning/
    (T1.3c, sessao de 03/08/2026). Renomeado de ReasoningEngine para
    EvidenceReasoningEngine para nao colidir com
    engines.reasoning.reasoning_engine.ReasoningEngine (motor
    estrutural, ja em uso por app.py). Investigacao (T1.3c) encontrou
    o mesmo padrao ja visto em T1.4a (validation) e T2.2 (evolution):
    NAO sao duas implementacoes concorrentes do mesmo ReasoningEngine
    -- sao dois motores complementares. Este (evidence-based) recebe
    so evidence_store, opera sobre pares de IECContract, gera
    inferencias e nunca toca o grafo. O estrutural (graph-based)
    recebe graph, opera sobre a estrutura do grafo inteiro (conexoes,
    conflitos, propagacao de confianca). O roadmap original presumia
    que T1.3c exigia "decidir qual e a oficial" -- nao exige: os dois
    ja sao complementares e continuam existindo lado a lado, mesma
    conclusao do T1.4a para validation/. Nenhum consumidor de producao
    real usava o caminho antigo antes desta migracao (so api/api.py,
    ja documentado como legado quebrado).
    """


    def __init__(
        self,
        evidence_store: EvidenceStore,
    ) -> None:
        """
        Initializes the reasoning engine.
        """

        if not isinstance(
            evidence_store,
            EvidenceStore,
        ):
            raise TypeError(
                "evidence_store must be an EvidenceStore."
            )

        self.evidence_store = evidence_store

        self.inferences: List[
            Dict[str, Any]
        ] = []

        self.history: List[
            Dict[str, Any]
        ] = []



    # ==========================================================
    # INTERNAL EVENT REGISTRATION
    # ==========================================================

    def _register_event(
        self,
        event: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Registers an internal engine event.
        """

        self.history.append(

            {

                "event":
                    event,

                "details":
                    details,

                "timestamp":
                    datetime.now(
                        UTC
                    ).isoformat(),

            }

        )



    # ==========================================================
    # ANALYZE IEC
    # ==========================================================

    def analyze_iec(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Analyzes a single IEC.

        Evaluates:

        - associated evidences;
        - epistemic strength;
        - support level;
        - available scientific context.
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

        evidence_strength = (

            self.evidence_store
            .compute_evidence_strength(
                iec.iec_id
            )

        )

        epistemic_state = (

            self._determine_state(
                evidence_strength,
                evidence_count,
            )

        )

        analysis = {

            "iec_id":
                iec.iec_id,

            "statement":
                iec.statement,

            "evidence_count":
                evidence_count,

            "evidence_strength":
                evidence_strength,

            "epistemic_state":
                epistemic_state,

        }

        self._register_event(
            "iec_analyzed",
            analysis,
        )

        return analysis



    # ==========================================================
    # DETERMINE EPISTEMIC STATE
    # ==========================================================

    def _determine_state(
        self,
        strength: float,
        evidence_count: int,
    ) -> str:
        """
        Determines the current epistemic state.
        """

        if evidence_count == 0:
            return "UNKNOWN"

        if strength >= 0.75:
            return "SUPPORTED"

        if strength >= 0.50:
            return "PLAUSIBLE"

        if strength >= 0.25:
            return "UNCERTAIN"

        return "WEAK"
    # ==========================================================
    # GENERATE INFERENCE
    # ==========================================================

    def generate_inference(
        self,
        source_iec: IECContract,
        target_iec: IECContract,
        relation: str,
        confidence: float,
    ) -> Dict[str, Any]:
        """
        Creates an inference relating two IECs.

        An inference is not a fact.
        It is a derived epistemological relation.
        """

        if not isinstance(
            source_iec,
            IECContract,
        ):
            raise TypeError(
                "source_iec must be an IECContract."
            )

        if not isinstance(
            target_iec,
            IECContract,
        ):
            raise TypeError(
                "target_iec must be an IECContract."
            )

        if not isinstance(
            relation,
            str,
        ):
            raise TypeError(
                "relation must be a string."
            )

        if not relation.strip():
            raise ValueError(
                "relation cannot be empty."
            )

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise TypeError(
                "confidence must be numeric."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
            )

        inference = {

            "source_iec":
                source_iec.iec_id,

            "target_iec":
                target_iec.iec_id,

            "relation":
                relation.strip(),

            "confidence":
                float(confidence),

            "created_at":
                datetime.now(
                    UTC
                ).isoformat(),

        }

        self.inferences.append(
            inference
        )

        self._register_event(
            "inference_generated",
            inference,
        )

        return inference



    # ==========================================================
    # COMPARE IECs
    # ==========================================================

    def compare_iec(
        self,
        iec_a: IECContract,
        iec_b: IECContract,
    ) -> Dict[str, Any]:
        """
        Compares the scientific support
        between two IECs.
        """

        if not isinstance(
            iec_a,
            IECContract,
        ):
            raise TypeError(
                "iec_a must be an IECContract."
            )

        if not isinstance(
            iec_b,
            IECContract,
        ):
            raise TypeError(
                "iec_b must be an IECContract."
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

            "support_a":
                strength_a,

            "support_b":
                strength_b,

            "stronger":
                stronger,

        }

        self._register_event(
            "iec_comparison",
            result,
        )

        return result



    # ==========================================================
    # DISCOVER PATTERNS
    # ==========================================================

    def discover_patterns(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Searches for recurring patterns
        among evidences.
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

        if not evidences:

            return {

                "iec_id":
                    iec.iec_id,

                "patterns":
                    [],

                "status":
                    "NO_DATA",

            }

        sources: Dict[
            str,
            int,
        ] = {}

        types: Dict[
            str,
            int,
        ] = {}

        for evidence in evidences:

            source = evidence.source

            sources[source] = (

                sources.get(
                    source,
                    0,
                )
                + 1

            )

            evidence_type = (
                evidence.evidence_type
            )

            types[evidence_type] = (

                types.get(
                    evidence_type,
                    0,
                )
                + 1

            )

        patterns: List[
            Dict[str, Any]
        ] = []

        for source, count in sources.items():

            if count > 1:

                patterns.append(

                    {

                        "pattern":
                            "repeated_source",

                        "source":
                            source,

                        "count":
                            count,

                    }

                )

        for evidence_type, count in types.items():

            if count > 1:

                patterns.append(

                    {

                        "pattern":
                            "repeated_evidence_type",

                        "type":
                            evidence_type,

                        "count":
                            count,

                    }

                )

        result = {

            "iec_id":
                iec.iec_id,

            "patterns":
                patterns,

            "status":
                "ANALYZED",

        }

        self._register_event(
            "patterns_discovered",
            result,
        )

        return result
    # ==========================================================
    # GENERATE RESEARCH QUESTIONS
    # ==========================================================

    def generate_research_questions(
        self,
        iec: IECContract,
    ) -> List[str]:
        """
        Generates scientific questions that may
        guide future investigations.
        """

        if not isinstance(
            iec,
            IECContract,
        ):
            raise TypeError(
                "iec must be an IECContract."
            )

        analysis = self.analyze_iec(
            iec
        )

        questions: List[str] = []

        if analysis["evidence_count"] == 0:

            questions.append(

                "Quais evidências científicas "
                "podem sustentar esta hipótese?"

            )

        elif analysis["epistemic_state"] == "UNCERTAIN":

            questions.append(

                "Quais experimentos podem "
                "aumentar a confiança desta IEC?"

            )

        elif analysis["epistemic_state"] == "PLAUSIBLE":

            questions.append(

                "Existem evidências independentes "
                "que confirmam este mecanismo?"

            )

        elif analysis["epistemic_state"] == "SUPPORTED":

            questions.append(

                "Quais limitações ainda existem "
                "neste conhecimento?"

            )

        self._register_event(

            "research_questions_generated",

            {

                "iec_id":
                    iec.iec_id,

                "questions":
                    list(
                        questions
                    ),

            },

        )

        return questions



    # ==========================================================
    # GET INFERENCES
    # ==========================================================

    def get_inferences(
        self,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Returns a copy of all generated
        inferences.
        """

        return list(
            self.inferences
        )



    # ==========================================================
    # GET INFERENCES FOR IEC
    # ==========================================================

    def get_inferences_for_iec(
        self,
        iec_id: str,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        Returns all inferences related
        to a specific IEC.
        """

        if not isinstance(
            iec_id,
            str,
        ):
            raise TypeError(
                "iec_id must be a string."
            )

        return [

            inference

            for inference
            in self.inferences

            if (

                inference["source_iec"]
                == iec_id

                or

                inference["target_iec"]
                == iec_id

            )

        ]



    # ==========================================================
    # SERIALIZATION
    # ==========================================================

    def to_dict(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Exports engine state.
        """

        return {

            "inferences":
                list(
                    self.inferences
                ),

            "history":
                list(
                    self.history
                ),

        }



    # ==========================================================
    # STATISTICS
    # ==========================================================

    def stats(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Returns engine metrics.
        """

        return {

            "total_inferences":
                len(
                    self.inferences
                ),

            "total_events":
                len(
                    self.history
                ),

            "engine":
                "EvidenceReasoningEngine",

            "status":
                "active",

        }



    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(
        self,
    ) -> Dict[
        str,
        Any,
    ]:
        """
        Returns operational health
        information for monitoring.
        """

        return {

            "healthy":
                True,

            "engine":
                "EvidenceReasoningEngine",

            "evidence_store":
                (
                    self.evidence_store
                    is not None
                ),

            "inferences":
                len(
                    self.inferences
                ),

            "history":
                len(
                    self.history
                ),

        }



    # ==========================================================
    # CLEAR
    # ==========================================================

    def clear(
        self,
    ) -> None:
        """
        Clears engine memory.
        """

        self.inferences.clear()

        self.history.clear()



    # ==========================================================
    # DEBUG
    # ==========================================================

    def __repr__(
        self,
    ) -> str:

        state = self.stats()

        return (

            f"<EvidenceReasoningEngine "
            f"inferences={state['total_inferences']} "
            f"events={state['total_events']} "
            f"status={state['status']}>"

        )
