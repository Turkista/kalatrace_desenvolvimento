from typing import Dict, Any, List
from datetime import datetime, UTC

from engines.cognitive_orchestrator.workflow import COGNITIVE_STATES


class CycleCoordinator:
    """
    Cycle Coordinator

    Mantém o estado cognitivo de cada ciclo (um ciclo por IEC
    nova, DOCUMENTO 26 Art. 5º) e o histórico completo de
    decisões tomadas durante ele (Art. 9º: "Toda decisão tomada
    durante um ciclo deverá ser registrada" -- horário, módulo
    responsável, entradas utilizadas, evidências consideradas,
    decisões produzidas, justificativas, alterações
    realizadas).

    Não executa nenhum passo do ciclo -- isso é
    responsabilidade de CyclePipeline (pipeline.py), que chama
    este módulo para registrar o que fez.
    """

    def __init__(self):
        # ciclos, por iec_id
        self.cycles: Dict[str, Dict[str, Any]] = {}

    # ==========================================================
    # 1. INICIAR CICLO (Art. 5º: "Cada novo conhecimento... 
    #    iniciará automaticamente um ciclo científico")
    # ==========================================================

    def start_cycle(self, iec_id: str, triggering_event: str) -> Dict[str, Any]:
        """Inicia um novo ciclo cognitivo para uma IEC."""
        cycle = {
            "iec_id": iec_id,
            "triggering_event": triggering_event,
            "state": "NOVO_CONHECIMENTO",
            "steps": [],
            "started_at": datetime.now(UTC).isoformat(),
            "ended_at": None,
        }
        self.cycles[iec_id] = cycle
        return cycle

    # ==========================================================
    # 2. REGISTRAR PASSO (Art. 9º)
    # ==========================================================

    def record_step(
        self,
        iec_id: str,
        step: str,
        module: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        justification: str,
    ) -> Dict[str, Any]:
        """
        Registra a execução de um passo do ciclo.

        Campos exigidos pelo Art. 9º: horário (timestamp),
        módulo responsável (module), entradas utilizadas
        (inputs), decisões/alterações produzidas (outputs),
        justificativas (justification). "Evidências
        consideradas" fica dentro de inputs/outputs quando
        aplicável -- o artigo não define um campo estrutural
        separado para isso.
        """
        cycle = self._get_cycle(iec_id)

        entry = {
            "step": step,
            "module": module,
            "inputs": inputs,
            "outputs": outputs,
            "justification": justification,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        cycle["steps"].append(entry)

        return entry

    # ==========================================================
    # 3. TRANSITAR ESTADO (Art. 6º)
    # ==========================================================

    def transition_state(self, iec_id: str, new_state: str, reason: str) -> Dict[str, Any]:
        """Transita o estado cognitivo do ciclo (Art. 6º)."""
        if new_state not in COGNITIVE_STATES:
            raise ValueError(f"Estado cognitivo inválido: {new_state}")

        cycle = self._get_cycle(iec_id)
        old_state = cycle["state"]
        cycle["state"] = new_state

        self.record_step(
            iec_id=iec_id,
            step="TRANSICAO_DE_ESTADO",
            module="CycleCoordinator",
            inputs={"from": old_state},
            outputs={"to": new_state},
            justification=reason,
        )

        return cycle

    # ==========================================================
    # 4. ENCERRAR CICLO (Art. 5º: "O término do ciclo não
    #    representa o encerramento definitivo da investigação")
    # ==========================================================

    def end_cycle(self, iec_id: str) -> Dict[str, Any]:
        """
        Encerra a execução ativa do ciclo -- não é um estado
        final permanente (Art. 5º), só marca que o sistema
        parou de processar esta IEC até o próximo evento
        relevante (nova evidência, por exemplo).
        """
        cycle = self._get_cycle(iec_id)
        cycle["ended_at"] = datetime.now(UTC).isoformat()
        return cycle

    # ==========================================================
    # 5. CONSULTAS
    # ==========================================================

    def _get_cycle(self, iec_id: str) -> Dict[str, Any]:
        if iec_id not in self.cycles:
            raise ValueError(f"Nenhum ciclo iniciado para {iec_id}")
        return self.cycles[iec_id]

    def get_cycle(self, iec_id: str) -> Dict[str, Any]:
        """Retorna o ciclo de uma IEC."""
        return self._get_cycle(iec_id)

    def list_active_cycles(self) -> List[Dict[str, Any]]:
        """Lista ciclos ainda não encerrados."""
        return [c for c in self.cycles.values() if c["ended_at"] is None]

    def state_distribution(self) -> Dict[str, int]:
        """Conta ciclos por estado cognitivo atual."""
        distribution: Dict[str, int] = {}
        for cycle in self.cycles.values():
            state = cycle["state"]
            distribution[state] = distribution.get(state, 0) + 1
        return distribution

    def __repr__(self) -> str:
        return f"CycleCoordinator(cycles={len(self.cycles)})"
