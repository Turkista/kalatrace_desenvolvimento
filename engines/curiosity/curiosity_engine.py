"""
KALATRACE Engines

Curiosity Engine

Responsible for identifying scientific
knowledge gaps and generating research
opportunities.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore


class CuriosityEngine:
    """
    Scientific curiosity engine of KALATRACE.

    Responsible for identifying:

    - knowledge gaps;
    - weakly supported IECs;
    - research opportunities;
    - scientific questions.

    CuriosityEngine does not create answers.

    It creates investigation paths.
    """


    def __init__(
        self,
        evidence_store: EvidenceStore,
    ) -> None:

        if evidence_store is None:
            raise ValueError(
                "Evidence store is required."
            )

        self.evidence_store = evidence_store


        # Generated questions

        self.questions: List[
            Dict[str, Any]
        ] = []


        # Research history

        self.history: List[
            Dict[str, Any]
        ] = []


        # Research queue

        self.research_queue: List[
            Dict[str, Any]
        ] = []



    # ==========================================================
    # INTERNAL REGISTRATION
    # ==========================================================


    def _register_event(
        self,
        event: str,
        details: Dict[str, Any],
    ) -> None:
        """
        Registers internal engine activity.

        Future versions may publish these
        through the KALATRACE EventBus.
        """


        self.history.append(

            {
                "event":
                    event,

                "details":
                    details,

                "timestamp":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),

            }

        )



    # ==========================================================
    # 1. ANALYZE IEC KNOWLEDGE GAP
    # ==========================================================


    def analyze_gap(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Analyzes knowledge gaps
        existing in an IEC.

        Evaluates:

        - evidence quantity;
        - evidence strength;
        - investigation necessity.
        """


        if not isinstance(
            iec,
            IECContract,
        ):
            raise TypeError(
                "Object must implement IECContract."
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


        curiosity_level = (
            self._calculate_curiosity(
                evidence_count,
                strength,
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


            "curiosity_level":
                curiosity_level,

        }


        self._register_event(
            "gap_analyzed",
            result,
        )


        return result



    # ==========================================================
    # 2. CALCULATE CURIOSITY LEVEL
    # ==========================================================


    def _calculate_curiosity(
        self,
        evidence_count: int,
        strength: float,
    ) -> str:
        """
        Calculates investigation necessity.
        """


        if evidence_count <= 0:

            return "CRITICAL"


        if strength < 0.25:

            return "HIGH"


        if strength < 0.50:

            return "MEDIUM"


        if strength < 0.75:

            return "LOW"


        return "MINIMAL"
    # ==========================================================
    # 3. GENERATE RESEARCH QUESTIONS
    # ==========================================================


    def generate_questions(
        self,
        iec: IECContract,
    ) -> List[str]:
        """
        Generates scientific questions
        based on identified gaps.
        """


        gap = self.analyze_gap(
            iec
        )


        questions: List[str] = []


        curiosity = (
            gap["curiosity_level"]
        )


        if curiosity == "CRITICAL":

            questions.append(
                "Which scientific evidence "
                "can validate this IEC?"
            )

            questions.append(
                "Is there scientific literature "
                "related to this hypothesis?"
            )


        elif curiosity == "HIGH":

            questions.append(
                "Which experiments can "
                "increase confidence in this hypothesis?"
            )

            questions.append(
                "Are there independent studies "
                "supporting this mechanism?"
            )


        elif curiosity == "MEDIUM":

            questions.append(
                "Which variables may explain "
                "the current uncertainty?"
            )


        elif curiosity == "LOW":

            questions.append(
                "Which limitations still exist "
                "in this knowledge?"
            )


        self.questions.append(

            {
                "iec_id":
                    iec.iec_id,

                "questions":
                    questions,

                "created_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),

            }

        )


        self._register_event(

            "questions_generated",

            {
                "iec_id":
                    iec.iec_id,

                "count":
                    len(questions),

            }

        )


        return questions



    # ==========================================================
    # 4. PRIORITIZE RESEARCH
    # ==========================================================


    def prioritize_research(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Defines investigation priority
        based on curiosity level.
        """


        gap = self.analyze_gap(
            iec
        )


        level = (
            gap["curiosity_level"]
        )


        priority_map = {

            "CRITICAL": 1,

            "HIGH": 2,

            "MEDIUM": 3,

            "LOW": 4,

            "MINIMAL": 5,

        }


        result = {

            "iec_id":
                iec.iec_id,

            "priority":
                priority_map.get(
                    level,
                    5,
                ),

            "curiosity_level":
                level,

        }


        self._register_event(

            "research_prioritized",

            result,

        )


        return result



    # ==========================================================
    # 5. CREATE RESEARCH TASK
    # ==========================================================


    def create_research_task(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Creates an investigation task
        for the future Scientific Research Engine.
        """


        priority = (
            self.prioritize_research(
                iec
            )
        )


        questions = (
            self.generate_questions(
                iec
            )
        )


        task = {

            "task_id":
                f"RESEARCH-{len(self.questions) + 1}",


            "iec_id":
                iec.iec_id,


            "statement":
                iec.statement,


            "priority":
                priority["priority"],


            "curiosity_level":
                priority["curiosity_level"],


            "questions":
                questions,


            "status":
                "PENDING",


            "created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

        }


        self._register_event(

            "research_task_created",

            task,

        )


        return task



    # ==========================================================
    # 6. RESEARCH QUEUE
    # ==========================================================


    def add_to_research_queue(
        self,
        task: Dict[str, Any],
    ) -> None:
        """
        Adds a research task to queue.
        """


        if not isinstance(
            task,
            dict,
        ):
            raise TypeError(
                "Research task must be a dictionary."
            )


        self.research_queue.append(
            task
        )


        self._register_event(

            "task_added_to_queue",

            {
                "task_id":
                    task.get(
                        "task_id"
                    ),

            }

        )



    # ==========================================================
    # 7. REQUEST RESEARCH
    # ==========================================================


    def request_research(
        self,
        iec: IECContract,
    ) -> Dict[str, Any]:
        """
        Complete flow:

        IEC
         ↓
        Curiosity Analysis
         ↓
        Research Task
         ↓
        Queue
        """


        task = (
            self.create_research_task(
                iec
            )
        )


        self.add_to_research_queue(
            task
        )


        return task



    # ==========================================================
    # 8. GET RESEARCH QUEUE
    # ==========================================================


    def get_research_queue(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Returns pending research tasks.
        """


        return self.research_queue



    # ==========================================================
    # 9. UPDATE RESEARCH STATUS
    # ==========================================================


    def update_research_status(
        self,
        task_id: str,
        status: str,
    ) -> bool:
        """
        Updates research task status.
        """


        for task in self.research_queue:

            if task.get(
                "task_id"
            ) == task_id:


                task["status"] = status


                task["updated_at"] = (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                )


                self._register_event(

                    "research_status_updated",

                    {
                        "task_id":
                            task_id,

                        "status":
                            status,

                    }

                )


                return True



        return False



    # ==========================================================
    # 10. EXPORT STATE
    # ==========================================================


    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Exports engine state.
        """


        return {

            "questions":
                self.questions,


            "research_queue":
                self.research_queue,


            "history":
                self.history,

        }



    # ==========================================================
    # 11. STATISTICS
    # ==========================================================


    def stats(
        self,
    ) -> Dict[str, Any]:
        """
        Returns engine metrics.
        """


        return {

            "questions_generated":
                len(self.questions),


            "research_tasks":
                len(
                    self.research_queue
                ),


            "events":
                len(self.history),


            "engine":
                "CuriosityEngine",


            "status":
                "active",

        }



    # ==========================================================
    # 12. CLEAR MEMORY
    # ==========================================================


    def clear(
        self,
    ) -> None:
        """
        Clears engine memory.
        """


        self.questions.clear()

        self.history.clear()

        self.research_queue.clear()



    # ==========================================================
    # 13. DEBUG
    # ==========================================================


    def __repr__(
        self,
    ) -> str:

        state = self.stats()


        return (

            f"CuriosityEngine("
            f"questions={state['questions_generated']}, "
            f"tasks={state['research_tasks']}, "
            f"status={state['status']}"
            f")"

        )