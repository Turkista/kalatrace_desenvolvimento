from typing import Dict, Any

from contracts.iec_contract import IECContract
from engines.curiosity.curiosity_engine import CuriosityEngine
from agents.base_agent import Agent, AgentRole, OutputType


class CuriosityAgent(Agent):
    """
    Curiosity Agent

    Agente de IA (DOCUMENTO 6) com papel ESTRUTURAL (Art. 4º,
    papel GPT: "estruturar problemas... organizar hipóteses"),
    especializado em identificar lacunas de conhecimento e
    formular perguntas científicas.

    Empacota a saída do CuriosityEngine (já determinística e
    real -- analyze_gap, generate_questions) no formato de saída
    de agente exigido pelo Art. 2º (sempre classificada). Ver o
    docstring de Agent para a nota de escopo sobre isso não
    chamar um LLM de verdade.
    """

    def __init__(self, curiosity_engine: CuriosityEngine):
        super().__init__(
            agent_id="curiosity-agent",
            name="Curiosity Agent",
            role=AgentRole.ESTRUTURAL,
            responsibility="Identificar lacunas de conhecimento e formular perguntas científicas.",
        )
        self.curiosity_engine = curiosity_engine

    # ==========================================================
    # ANALISAR E SUGERIR (papel ESTRUTURAL)
    # ==========================================================

    def analyze_and_suggest(self, iec: IECContract) -> Dict[str, Any]:
        """Analisa a lacuna de uma IEC e produz uma sugestão de investigação, classificada."""
        gap = self.curiosity_engine.analyze_gap(iec)
        questions = self.curiosity_engine.generate_questions(iec)

        content = {
            "iec_id": iec.iec_id,
            "gap_analysis": gap,
            "questions": questions,
        }

        return self.produce_output(content, OutputType.SUGESTAO)

    def __repr__(self) -> str:
        return "CuriosityAgent()"
