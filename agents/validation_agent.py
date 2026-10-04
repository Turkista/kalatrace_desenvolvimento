from typing import Dict, Any

from validation.validation_engine import ValidationEngine
from agents.base_agent import Agent, AgentRole, OutputType


class ValidationAgent(Agent):
    """
    Validation Agent

    Agente de IA (DOCUMENTO 6) com papel CRITICO (Art. 4º, papel
    Claude: "identificação de inconsistências... avaliação
    epistemológica preliminar"), especializado em revisar a
    validação estrutural de uma IEC.

    Empacota a saída do ValidationEngine (já determinística e
    real -- validate_iec) no formato de saída de agente exigido
    pelo Art. 2º. Ver o docstring de Agent para a nota de escopo
    sobre isso não chamar um LLM de verdade -- em particular, a
    "avaliação epistemológica preliminar" aqui é o resultado
    numérico do ValidationEngine, não um julgamento gerado por
    IA generativa.
    """

    def __init__(self, validation_engine: ValidationEngine):
        super().__init__(
            agent_id="validation-agent",
            name="Validation Agent",
            role=AgentRole.CRITICO,
            responsibility="Revisar a validação estrutural e identificar inconsistências de uma IEC.",
        )
        self.validation_engine = validation_engine

    # ==========================================================
    # REVISAR VALIDAÇÃO (papel CRITICO)
    # ==========================================================

    def review_validation(self, iec_id: str) -> Dict[str, Any]:
        """Revisa a validação estrutural de uma IEC, produzindo análise crítica classificada."""
        result = self.validation_engine.validate_iec(iec_id)

        content = {
            "iec_id": iec_id,
            "validation_result": result,
        }

        return self.produce_output(content, OutputType.ANALISE_CRITICA)

    def __repr__(self) -> str:
        return "ValidationAgent()"
