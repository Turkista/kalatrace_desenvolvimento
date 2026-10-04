from typing import Dict, Any, List, Optional
from datetime import datetime, UTC


class ManualAcquisition:
    """
    Manual Acquisition

    Módulo de aquisição experimental manual do KALATRACE
    (DOCUMENTO 23, Seção 8.1 e Seção 11):

        "Responsável pela recepção de informações provenientes
        do pesquisador e da interface do MEDIKALAT. Não
        interpreta os dados. Apenas garante sua captura
        íntegra."

    Este módulo:

    - NÃO cria IECs (isso é responsabilidade do IECBuilder,
      Seção 11, ainda não implementado -- o chamador usa o
      resultado de capture() para, se quiser, construir a IEC
      via engines.base.base_engine.CoreEngine.create_iec, o
      construtor real já existente);
    - NÃO valida sustentação científica (isso é
      responsabilidade de camadas posteriores no fluxo do
      DOCUMENTO 23, Seção 10: Contextualização, Comparação,
      Validação);
    - NÃO interpreta o conteúdo -- só garante integridade
      estrutural da captura (campos obrigatórios presentes,
      não vazios) e rastreabilidade (Seção 4, objetivo:
      "preservar a origem e a rastreabilidade completa de
      todas as informações incorporadas").

    Escopo desta implementação (roadmap de estabilização,
    sessão de 07/08/2026): cobre as modalidades manuais
    listadas na Seção 8.1 do DOCUMENTO 23 (protocolos
    experimentais, observações laboratoriais, resultados
    positivos/negativos, hipóteses formuladas pelo
    pesquisador, etc.) de forma genérica -- um único formato
    de captura, com o tipo da submissão como um campo
    (submission_type), em vez de uma classe por tipo. O
    documento não exige tipos estruturalmente diferentes; a
    distinção de tipo é dado, não estrutura.
    """

    # Campos que toda submissão precisa ter para ser considerada
    # íntegra (Seção 8.1: origem sempre rastreável; Seção 4:
    # rastreabilidade completa).
    REQUIRED_FIELDS = ("statement", "submitted_by")

    def __init__(self):
        # capturas realizadas, por id -- nunca removidas
        # (mesmo princípio de DOCUMENTO 30, Princípio 8:
        # "histórico nunca é apagado")
        self.captures: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1

    # ==========================================================
    # 1. CAPTURAR SUBMISSÃO
    # ==========================================================

    def capture(
        self,
        statement: str,
        submitted_by: str,
        submission_type: str = "observacao",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Captura uma submissão manual do pesquisador ou da
        interface do MEDIKALAT.

        submission_type: livre, mas espelha os exemplos da
        Seção 8.1 do DOCUMENTO 23 -- "protocolo_experimental",
        "observacao_laboratorial", "resultado_positivo",
        "resultado_negativo", "hipotese", etc. Não é validado
        contra uma lista fechada: o documento lista exemplos,
        não uma enumeração fechada de tipos.

        Levanta ValueError se a submissão não tiver os campos
        obrigatórios (integridade estrutural) -- nunca por
        julgamento de mérito científico, que não é
        responsabilidade deste módulo.
        """
        payload = {
            "statement": statement,
            "submitted_by": submitted_by,
            "submission_type": submission_type,
            "metadata": metadata or {},
        }

        self._validate_integrity(payload)

        capture_id = f"CAPTURE-{self._next_id}"
        self._next_id += 1

        record = {
            "capture_id": capture_id,
            "statement": statement,
            "submitted_by": submitted_by,
            "submission_type": submission_type,
            "metadata": metadata or {},
            "status": "CAPTURED",
            "captured_at": datetime.now(UTC).isoformat(),
        }

        self.captures[capture_id] = record

        return record

    # ==========================================================
    # 2. VALIDAR INTEGRIDADE (não validação científica)
    # ==========================================================

    def _validate_integrity(self, payload: Dict[str, Any]):
        """
        Garante captura íntegra (Seção 8.1) -- checagem
        estrutural, não epistemológica: campos obrigatórios
        presentes e não vazios.
        """
        for field in self.REQUIRED_FIELDS:
            value = payload.get(field)
            if not value or not str(value).strip():
                raise ValueError(
                    f"Captura íntegra exige o campo '{field}' preenchido "
                    f"(DOCUMENTO 23, Seção 8.1)"
                )

    # ==========================================================
    # 3. CONSULTAS
    # ==========================================================

    def get_capture(self, capture_id: str) -> Dict[str, Any]:
        """Retorna uma captura pelo id."""
        if capture_id not in self.captures:
            raise ValueError(f"Captura {capture_id} não registrada")
        return self.captures[capture_id]

    def list_captures(self, submission_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista capturas, opcionalmente filtradas por tipo."""
        values = list(self.captures.values())
        if submission_type is None:
            return values
        return [c for c in values if c["submission_type"] == submission_type]

    def mark_promoted(self, capture_id: str, iec_id: str) -> Dict[str, Any]:
        """
        Marca uma captura como já promovida a IEC (via
        CoreEngine.create_iec, fora deste módulo -- ver
        docstring da classe). Preserva rastreabilidade entre a
        submissão bruta e a IEC que ela originou.
        """
        record = self.get_capture(capture_id)
        record["status"] = "PROMOTED_TO_IEC"
        record["promoted_iec_id"] = iec_id
        return record

    def stats(self) -> Dict[str, Any]:
        """Estatísticas das capturas realizadas."""
        by_status: Dict[str, int] = {}
        for c in self.captures.values():
            by_status[c["status"]] = by_status.get(c["status"], 0) + 1

        return {
            "total_captures": len(self.captures),
            "by_status": by_status,
        }

    def __repr__(self) -> str:
        return f"ManualAcquisition(captures={len(self.captures)})"
