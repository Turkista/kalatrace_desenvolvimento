from typing import Dict, Any, Optional
from datetime import datetime, UTC
from enum import Enum
import uuid


class AgentRole(str, Enum):
    """
    Papel do agente (DOCUMENTO 6, Título III, Art. 4º): os dois
    papéis oficialmente nomeados no documento são GPT
    ("estruturar problemas... organizar hipóteses... sugerir
    conexões") e Claude ("análise crítica... identificação de
    inconsistências... refinamento argumentativo"). O documento
    generaliza os dois como papéis (não como produtos específicos
    de IA), abrindo espaço para "Agentes Futuros" com o mesmo
    papel estrutural ou crítico.
    """
    ESTRUTURAL = "ESTRUTURAL"  # papel GPT: estrutura, organiza, sugere
    CRITICO = "CRITICO"        # papel Claude: analisa, critica, refina


class OutputType(str, Enum):
    """
    Classificação obrigatória de toda saída de um agente
    (DOCUMENTO 6, Art. 2º): "Nenhuma Inteligência Artificial
    constitui fonte autônoma de verdade científica. Toda saída
    produzida deverá ser tratada como": hipótese, interpretação,
    sugestão, análise crítica ou proposta estrutural. Uma saída
    de agente sem uma dessas cinco classificações não é permitida
    por esta implementação.
    """
    HIPOTESE = "HIPOTESE"
    INTERPRETACAO = "INTERPRETACAO"
    SUGESTAO = "SUGESTAO"
    ANALISE_CRITICA = "ANALISE_CRITICA"
    PROPOSTA_ESTRUTURAL = "PROPOSTA_ESTRUTURAL"


class Agent:
    """
    Base Agent

    Classe-base de todo agente de IA do KALATRACE (DOCUMENTO 6 --
    Arquitetura de Acoplamento de Inteligência Artificial).

    Princípios aplicados nesta classe:

    - Art. 1º/2º: "nenhuma Inteligência Artificial constitui
      fonte autônoma de verdade científica" -- toda saída passa
      por produce_output(), que exige um OutputType (nunca texto
      solto, não classificado).
    - Art. 8º: "nenhum agente poderá comunicar-se diretamente
      com outro. Toda comunicação ocorrerá exclusivamente por
      intermédio do Orquestrador" -- por design, Agent não importa
      nem referencia nenhuma outra classe Agent. Um agente só
      produz registros de interação; quem os consome (hoje, quem
      chama o agente diretamente; no futuro, o Orquestrador
      Cognitivo de IA, Documento 6 Título IV, ainda não
      implementado -- ver agents/orchestrator_agent.py) decide o
      que fazer com eles.
    - Art. 9º: cada interação produzida tem identificador único,
      registro temporal, agente emissor, agente destinatário e
      histórico completo -- campos de InteractionRecord abaixo.

    Escopo honesto desta implementação (roadmap de estabilização,
    sessão de 09/08/2026): os agentes concretos que herdam desta
    classe (curiosity_agent.py, reasoning_agent.py,
    research_agent.py, validation_agent.py) empacotam a saída de
    um Engine determinístico já existente no formato exigido pelo
    Art. 2º -- não chamam um modelo de linguagem de verdade (GPT
    ou Claude reais). Este ambiente de execução não tem acesso à
    rede para chamar uma API de IA externa. A classificação e o
    texto de interpretação são gerados por regra, não por um
    modelo -- documentado em cada agente concreto, nunca
    apresentado como se fosse saída real de um LLM.
    """

    def __init__(self, agent_id: str, name: str, role: AgentRole, responsibility: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.responsibility = responsibility
        self.interaction_history: list = []

    # ==========================================================
    # PRODUZIR SAÍDA CLASSIFICADA (Art. 2º)
    # ==========================================================

    def produce_output(
        self,
        content: Dict[str, Any],
        output_type: OutputType,
        destination: str = "ORQUESTRADOR",
    ) -> Dict[str, Any]:
        """
        Produz uma saída de agente, sempre classificada (Art.
        2º) e sempre registrada como interação rastreável (Art.
        9º). destination é sempre "ORQUESTRADOR" por padrão --
        Art. 8º: nenhum agente se comunica direto com outro.
        """
        if not isinstance(output_type, OutputType):
            raise TypeError(
                "output_type precisa ser um OutputType -- toda saída de agente "
                "deve ser classificada (DOCUMENTO 6, Art. 2º)"
            )

        record = {
            "interaction_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "emitting_agent": self.agent_id,
            "destination": destination,
            "output_type": output_type.value,
            "content": content,
            "version": len(self.interaction_history) + 1,
        }

        self.interaction_history.append(record)

        return record

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_interaction_history(self) -> list:
        """Histórico completo de interações deste agente (Art. 9º)."""
        return self.interaction_history

    def describe(self) -> Dict[str, Any]:
        """Descrição do agente, no formato exigido pelo Art. 4º para 'Agentes Futuros'."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "responsibility": self.responsibility,
        }

    def __repr__(self) -> str:
        return f"Agent(id={self.agent_id}, role={self.role.value})"
