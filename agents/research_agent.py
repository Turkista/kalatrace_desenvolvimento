from typing import Dict, Any

from engines.scientific_research.scientific_research_engine import ScientificResearchEngine
from agents.base_agent import Agent, AgentRole, OutputType


class ResearchAgent(Agent):
    """
    Research Agent

    Agente de IA (DOCUMENTO 6) com papel ESTRUTURAL (Art. 4º,
    papel GPT: "sintetizar literatura... sugerir conexões"),
    especializado em organizar planos de investigação a partir
    de tarefas de pesquisa.

    Empacota a saída do ScientificResearchEngine (já
    determinística e real -- create_research_plan) no formato de
    saída de agente exigido pelo Art. 2º, como proposta
    estrutural. Ver o docstring de Agent para a nota de escopo
    sobre isso não chamar um LLM de verdade -- em particular,
    "sintetizar literatura" continua fora do escopo desta
    implementação: o ScientificResearchEngine não faz busca
    externa (ver ENGINE-007), então este agente organiza o
    plano de investigação interno, não sintetiza artigos.
    """

    def __init__(self, research_engine: ScientificResearchEngine):
        super().__init__(
            agent_id="research-agent",
            name="Research Agent",
            role=AgentRole.ESTRUTURAL,
            responsibility="Organizar planos de investigação a partir de tarefas de pesquisa.",
        )
        self.research_engine = research_engine

    # ==========================================================
    # PROPOR PLANO (papel ESTRUTURAL)
    # ==========================================================

    def propose_plan(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Organiza um plano de investigação a partir de uma tarefa, como proposta estrutural."""
        plan = self.research_engine.create_research_plan(task)

        content = {
            "task": task,
            "plan": plan,
        }

        return self.produce_output(content, OutputType.PROPOSTA_ESTRUTURAL)

    def __repr__(self) -> str:
        return "ResearchAgent()"
