from typing import Dict, Any

from engines.reasoning.reasoning_engine import ReasoningEngine
from agents.base_agent import Agent, AgentRole, OutputType


class ReasoningAgent(Agent):
    """
    Reasoning Agent

    Agente de IA (DOCUMENTO 6) com papel CRITICO (Art. 4º, papel
    Claude: "revisão lógica... refinamento argumentativo"),
    especializado em revisar e explicar as conexões que o
    ReasoningEngine já estabeleceu no grafo.

    Empacota a saída do ReasoningEngine (já determinística e
    real -- explain_connection) no formato de saída de agente
    exigido pelo Art. 2º. Ver o docstring de Agent para a nota
    de escopo sobre isso não chamar um LLM de verdade.
    """

    def __init__(self, reasoning_engine: ReasoningEngine):
        super().__init__(
            agent_id="reasoning-agent",
            name="Reasoning Agent",
            role=AgentRole.CRITICO,
            responsibility="Revisar logicamente e explicar as conexões estabelecidas no grafo.",
        )
        self.reasoning_engine = reasoning_engine

    # ==========================================================
    # REVISAR CONEXÃO (papel CRITICO)
    # ==========================================================

    def review_connection(self, node_a_id: str, node_b_id: str) -> Dict[str, Any]:
        """Revisa logicamente a conexão entre dois nós, produzindo análise crítica classificada."""
        explanation = self.reasoning_engine.explain_connection(node_a_id, node_b_id)

        content = {
            "node_a_id": node_a_id,
            "node_b_id": node_b_id,
            "explanation": explanation,
        }

        return self.produce_output(content, OutputType.ANALISE_CRITICA)

    def __repr__(self) -> str:
        return "ReasoningAgent()"
