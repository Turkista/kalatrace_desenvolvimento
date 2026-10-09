from typing import Dict, Any, List
from datetime import datetime, UTC

from contracts.iec_contract import IECContract


class StateTransitionManager:
    """
    State Transition Manager

    Responsável exclusivamente pelo estado epistemológico
    de cada IEC acompanhada pelo KnowledgeEvolutionEngine (KEE)
    e pelas transições entre esses estados.

    Não calcula evolução, não lê evidências, não gera
    diagnóstico -- essa é responsabilidade do
    EvolutionAnalyzer (evolution_analyzer.py), que usa este
    módulo como fonte de estado.

    Extraído de KnowledgeEvolutionEngine (roadmap de
    estabilização, ENGINE-006, sessão de 07/08/2026). Métodos
    movidos aqui sem alteração de comportamento: register_iec,
    get_state, update_state, list_registered_iecs,
    state_distribution, clear. KnowledgeEvolutionEngine
    (knowledge_evolution_engine.py) continua sendo o ponto de
    entrada público -- ele compõe este módulo internamente e
    mantém exatamente a mesma API externa de antes do split.
    """

    def __init__(self):
        # estados atuais das IECs
        self.iec_states: Dict[str, Dict[str, Any]] = {}

    # ==========================================================
    # 1. REGISTRAR IEC
    # ==========================================================

    def register_iec(self, iec: IECContract) -> Dict[str, Any]:
        """
        Registra uma IEC no sistema de evolução do conhecimento.

        Toda IEC inicia como: UNKNOWN
        """
        if not isinstance(iec, IECContract):
            raise TypeError("O objeto precisa ser um IECContract")

        state = {
            "iec_id": iec.iec_id,
            "statement": iec.statement,
            "current_state": "UNKNOWN",
            "previous_states": [],
            "created_at": iec.created_at or datetime.now(UTC).isoformat(),
        }

        self.iec_states[iec.iec_id] = state

        return state

    # ==========================================================
    # 2. OBTER ESTADO ATUAL
    # ==========================================================

    def get_state(self, iec_id: str) -> Dict[str, Any]:
        """Retorna o estado atual de uma IEC."""
        if iec_id not in self.iec_states:
            raise ValueError(f"IEC {iec_id} não registrada")

        return self.iec_states[iec_id]

    # ==========================================================
    # 3. ALTERAR ESTADO DO CONHECIMENTO
    # ==========================================================

    def update_state(self, iec_id: str, new_state: str, reason: str) -> Dict[str, Any]:
        """
        Atualiza o estado epistemológico de uma IEC.
        Mantém histórico das mudanças.

        Retorna o estado atualizado (o chamador -- EvolutionAnalyzer
        ou o próprio KnowledgeEvolutionEngine -- decide se/como
        registra o evento em seu próprio histórico de eventos).
        """
        current = self.get_state(iec_id)
        old_state = current["current_state"]

        transition = {
            "from": old_state,
            "to": new_state,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        current["previous_states"].append(transition)
        current["current_state"] = new_state

        return current

    # ==========================================================
    # 4. LISTAR IECs REGISTRADAS
    # ==========================================================

    def list_registered_iecs(self) -> List[str]:
        """Retorna todas as IECs acompanhadas."""
        return list(self.iec_states.keys())

    # ==========================================================
    # 5. CONTAGEM POR ESTADO
    # ==========================================================

    def state_distribution(self) -> Dict[str, int]:
        """Mostra quantas IECs existem em cada estado epistemológico."""
        distribution = {}
        for state in self.iec_states.values():
            current = state["current_state"]
            distribution[current] = distribution.get(current, 0) + 1
        return distribution

    # ==========================================================
    # 6. EXPORTAR / RESTAURAR ESTADO
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Exporta o estado epistemológico atual para persistência."""
        return {
            "iec_states": {
                iec_id: dict(state)
                for iec_id, state in self.iec_states.items()
            }
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Reconstrói estados epistemológicos a partir de um snapshot."""
        if not isinstance(snapshot, dict):
            raise TypeError("O snapshot precisa ser um dicionário")

        restored = snapshot.get("iec_states", snapshot)
        if not isinstance(restored, dict):
            raise ValueError("Snapshot de estados inválido")

        self.iec_states.clear()

        for iec_id, state in restored.items():
            if not isinstance(state, dict):
                raise ValueError(f"Estado inválido para IEC {iec_id}")
            if state.get("iec_id") != iec_id:
                raise ValueError(f"Snapshot inconsistente para IEC {iec_id}")
            if not state.get("current_state"):
                raise ValueError(f"IEC {iec_id} sem estado atual")

            self.iec_states[iec_id] = {
                "iec_id": state["iec_id"],
                "statement": state.get("statement", ""),
                "current_state": state["current_state"],
                "previous_states": list(state.get("previous_states", [])),
                "created_at": state.get("created_at"),
            }

    @classmethod
    def from_dict(cls, snapshot: Dict[str, Any]) -> "StateTransitionManager":
        manager = cls()
        manager.restore(snapshot)
        return manager

    # ==========================================================
    # 7. LIMPAR ESTADO
    # ==========================================================

    def clear(self):
        """Limpa todos os estados."""
        self.iec_states.clear()

    # ==========================================================
    # 8. DEBUG
    # ==========================================================

    def __repr__(self) -> str:
        return f"StateTransitionManager(iecs={len(self.iec_states)})"
