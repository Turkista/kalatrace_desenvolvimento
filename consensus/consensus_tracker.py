from typing import Dict, Any, List, Optional
from datetime import datetime, UTC


class ConsensusTracker:
    """
    Consensus Tracker

    Guarda o histórico de classificações de consenso científico
    (campo `scientific_consensus`, Panorama Científico, DOCUMENTO
    23 Seção 15.6) de cada IEC ao longo do tempo -- nunca apagado,
    mesmo princípio geral do DOCUMENTO 30 já usado em
    ContextTimeline e ResearchPlanner.

    Não calcula o consenso (isso é ContextBuilder._assess_consensus,
    dentro do Scientific Context Reconstruction) -- só registra o
    que a SCR já concluiu e observa como essa classificação muda
    entre reconstruções sucessivas da mesma IEC.
    """

    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}

    def record(self, iec_id: str, consensus_state: str, divergent_count: int, convergent_count: int) -> Dict[str, Any]:
        """Registra uma classificação de consenso vinda de um Panorama Científico (SCR)."""
        entry = {
            "consensus_state": consensus_state,
            "divergent_count": divergent_count,
            "convergent_count": convergent_count,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        self.history.setdefault(iec_id, []).append(entry)
        return entry

    def get_history(self, iec_id: str) -> List[Dict[str, Any]]:
        return self.history.get(iec_id, [])

    def latest(self, iec_id: str) -> Optional[Dict[str, Any]]:
        entries = self.history.get(iec_id, [])
        return entries[-1] if entries else None

    def detect_shift(self, iec_id: str) -> Optional[Dict[str, Any]]:
        """
        Compara as duas últimas classificações registradas para
        esta IEC. Se mudaram, é uma mudança de paradigma no sentido
        do DOCUMENTO 23 Seção 16 ("o contexto científico construído
        pela SCR nunca deverá ser considerado definitivo"). Precisa
        de ao menos 2 registros -- com 0 ou 1, não há o que comparar
        (retorna None, não um "sem mudança" fabricado).
        """
        entries = self.history.get(iec_id, [])
        if len(entries) < 2:
            return None

        previous, current = entries[-2], entries[-1]
        if previous["consensus_state"] == current["consensus_state"]:
            return None

        return {
            "iec_id": iec_id,
            "from_state": previous["consensus_state"],
            "to_state": current["consensus_state"],
            "detected_at": current["recorded_at"],
        }

    def all_tracked_iecs(self) -> List[str]:
        return list(self.history.keys())

    def __repr__(self) -> str:
        return f"ConsensusTracker(iecs={len(self.history)})"
