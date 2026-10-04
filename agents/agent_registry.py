from typing import Dict, Any, List

from agents.base_agent import Agent


class AgentRegistry:
    """
    Agent Registry

    Registro dos agentes de IA do sistema (DOCUMENTO 6, Título
    III, Art. 4º -- "Agentes Futuros"): "Cada novo agente deverá
    possuir documentação própria contendo: finalidade; escopo;
    entradas; saídas; critérios de atuação."

    Este registro exige essa documentação no ato de registrar um
    agente -- não é opcional, é a exigência formal do artigo.
    """

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}

    # ==========================================================
    # REGISTRAR AGENTE (Art. 4º)
    # ==========================================================

    def register(
        self,
        agent: Agent,
        finalidade: str,
        escopo: str,
        entradas: str,
        saidas: str,
        criterios_de_atuacao: str,
    ) -> Dict[str, Any]:
        """Registra um agente com a documentação exigida pelo Art. 4º."""
        entry = {
            **agent.describe(),
            "finalidade": finalidade,
            "escopo": escopo,
            "entradas": entradas,
            "saidas": saidas,
            "criterios_de_atuacao": criterios_de_atuacao,
        }
        self.agents[agent.agent_id] = entry
        return entry

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get(self, agent_id: str) -> Dict[str, Any]:
        """Retorna a documentação de um agente registrado."""
        if agent_id not in self.agents:
            raise ValueError(f"Agente {agent_id} não registrado")
        return self.agents[agent_id]

    def list_agents(self) -> List[Dict[str, Any]]:
        """Lista todos os agentes registrados."""
        return list(self.agents.values())

    def list_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Lista agentes por papel (ESTRUTURAL ou CRITICO -- Art. 4º)."""
        return [a for a in self.agents.values() if a["role"] == role]

    def __repr__(self) -> str:
        return f"AgentRegistry(agents={len(self.agents)})"
