from typing import Dict, Any, List
from datetime import datetime, UTC


class ContextTimeline:
    """
    Context Timeline

    Registra o histórico de reconstruções de contexto científico
    de cada IEC (DOCUMENTO 23, Seção 16, "Contexto Científico
    Dinâmico": "o contexto científico construído pela SCR nunca
    deverá ser considerado definitivo... sempre que novas
    publicações forem incorporadas, a reconstrução do contexto
    poderá ser executada novamente").

    Não decide QUANDO reconstruir -- só registra que uma
    reconstrução aconteceu, e mantém o histórico (nunca apagado,
    mesmo princípio geral do DOCUMENTO 30).
    """

    def __init__(self):
        self.history: Dict[str, List[Dict[str, Any]]] = {}

    def record_reconstruction(self, iec_id: str, panorama_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Registra que uma reconstrução de contexto aconteceu para uma IEC."""
        entry = {
            "iec_id": iec_id,
            "summary": panorama_summary,
            "reconstructed_at": datetime.now(UTC).isoformat(),
        }
        self.history.setdefault(iec_id, []).append(entry)
        return entry

    def get_history(self, iec_id: str) -> List[Dict[str, Any]]:
        """Retorna todas as reconstruções já feitas para uma IEC."""
        return self.history.get(iec_id, [])

    def reconstruction_count(self, iec_id: str) -> int:
        """Quantas vezes o contexto desta IEC já foi reconstruído."""
        return len(self.history.get(iec_id, []))

    def __repr__(self) -> str:
        return f"ContextTimeline(iecs={len(self.history)})"
