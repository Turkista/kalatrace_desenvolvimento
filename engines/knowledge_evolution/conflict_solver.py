from typing import Dict, Any, List, Optional
from datetime import datetime, UTC

from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.state_transition import StateTransitionManager


# ==========================================================
# VOCABULÁRIO OFICIAL (DOCUMENTO 3 — Manual Operacional do
# Sistema MEDIKALAT + KALATRACE, Capítulo V "Dos Conflitos
# Epistêmicos" e Capítulo VI "Da Resolução de Conflitos",
# Art. 73º a 77º)
# ==========================================================

# Art. 74º — Conflitos são classificados como:
CONFLICT_LEVELS = (
    "LEVE",       # I — diferença interpretativa
    "MODERADO",   # II — dados divergentes
    "CRITICO",    # III — contradição estrutural
)

# Art. 76º — A resolução de conflitos pode ocorrer por:
RESOLUTION_MECHANISMS = (
    "NOVA_EVIDENCIA_EXPERIMENTAL",       # I
    "REVISAO_METODOLOGICA",              # II
    "INTEGRACAO_MULTIPLAS_FONTES",       # III
    "RECLASSIFICACAO_NIVEL_EVIDENCIA",   # IV
    "SEPARACAO_DOMINIOS_VALIDADE",       # V
)

# Art. 77º — resultado final de um conflito resolvido
RESOLUTION_OUTCOMES = (
    "RESOLVIDO_POR_INTEGRACAO",
    "RESOLVIDO_POR_REFUTACAO",
)


class ConflictSolver:
    """
    Conflict Solver

    Responsável por registrar, classificar e resolver
    conflitos epistemológicos entre IECs, seguindo as regras
    formais do DOCUMENTO 3 (Manual Operacional do Sistema
    MEDIKALAT + KALATRACE):

    - Art. 73º: um conflito epistemológico ocorre quando dois
      ou mais nós apresentam evidências incompatíveis;
    - Art. 74º: conflitos são classificados em LEVE, MODERADO
      ou CRITICO;
    - Art. 75º: conflitos não são erros -- são mecanismos de
      evolução do sistema, e devem permanecer ativos até
      resolução ou reclassificação;
    - Art. 76º: a resolução pode ocorrer por 5 mecanismos
      (ver RESOLUTION_MECHANISMS acima);
    - Art. 77º: um conflito resolvido nunca é apagado, só
      marcado como resolvido por integração ou por refutação
      (RESOLUTION_OUTCOMES acima) -- mesmo princípio geral do
      DOCUMENTO 30 ("histórico nunca é apagado").

    Escopo desta implementação (roadmap de estabilização,
    sessão de 07/08/2026): o DOCUMENTO 3 define COM QUE
    CATEGORIAS um conflito é classificado e COMO ele pode ser
    resolvido -- não define um algoritmo automático para
    DETECTAR que duas IECs estão em contradição semântica (Art.
    73º diz "apresentam evidências incompatíveis", mas não
    especifica como determinar incompatibilidade a partir do
    conteúdo). Detectar contradição semântica automaticamente
    é um problema de NLP/inferência separado, fora do escopo
    de uma reorganização de código, e nenhum documento
    consultado até agora especifica esse algoritmo.

    Por isso, este módulo assume que o conflito já foi
    identificado por quem chama (um Engine de inferência, o
    ReasoningEngine, ou um humano) -- via register_conflict(),
    informando quais duas IECs conflitam. A partir daí, a
    classificação de severidade (LEVE/MODERADO/CRITICO) É
    automática, calculada a partir da força de evidência de
    cada lado (evidence_store.compute_evidence_strength) --
    essa fórmula específica de severidade não vem do
    DOCUMENTO 3 (que só define as 3 categorias qualitativas,
    Art. 74º), é a interpretação desta implementação: quando
    os dois lados têm sustentação forte (>= 0.70) e mesmo
    assim se contradizem, isso é uma contradição estrutural
    genuína (CRITICO); quando só um lado tem sustentação
    razoável (>= 0.50), é uma divergência de dados assimétrica
    (MODERADO); no restante, tratado como diferença
    interpretativa (LEVE). Os limiares (0.70 / 0.50) seguem o
    mesmo estilo das faixas já usadas em
    evolution_analyzer.py::_suggest_state -- sujeitos a
    calibração futura.
    """

    def __init__(
        self,
        state_manager: StateTransitionManager,
        evidence_store: EvidenceStore,
    ):
        self.state_manager = state_manager
        self.evidence_store = evidence_store

        # conflitos registrados, por id
        self.conflicts: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1

    # ==========================================================
    # 1. REGISTRAR CONFLITO (Art. 73º)
    # ==========================================================

    def register_conflict(
        self,
        iec_a_id: str,
        iec_b_id: str,
        description: str,
    ) -> Dict[str, Any]:
        """
        Registra um conflito epistemológico entre duas IECs.

        A identificação de QUE as duas IECs conflitam é
        responsabilidade de quem chama (ver docstring da
        classe) -- este método classifica a severidade e
        mantém o conflito ativo (Art. 75º).
        """
        if iec_a_id not in self.state_manager.iec_states:
            raise ValueError(f"IEC {iec_a_id} não registrada")
        if iec_b_id not in self.state_manager.iec_states:
            raise ValueError(f"IEC {iec_b_id} não registrada")

        level = self._classify_severity(iec_a_id, iec_b_id)

        conflict_id = f"CONFLICT-{self._next_id}"
        self._next_id += 1

        record = {
            "conflict_id": conflict_id,
            "iec_a_id": iec_a_id,
            "iec_b_id": iec_b_id,
            "description": description,
            "level": level,
            "status": "ATIVO",
            "resolution": None,
            "created_at": datetime.now(UTC).isoformat(),
            "resolved_at": None,
        }

        self.conflicts[conflict_id] = record

        return record

    # ==========================================================
    # 2. CLASSIFICAR SEVERIDADE (Art. 74º)
    # ==========================================================

    def _classify_severity(self, iec_a_id: str, iec_b_id: str) -> str:
        """Ver nota de escopo no docstring da classe sobre estes limiares."""
        strength_a = self.evidence_store.compute_evidence_strength(iec_a_id)
        strength_b = self.evidence_store.compute_evidence_strength(iec_b_id)

        if strength_a >= 0.70 and strength_b >= 0.70:
            return "CRITICO"

        if strength_a >= 0.50 or strength_b >= 0.50:
            return "MODERADO"

        return "LEVE"

    # ==========================================================
    # 3. RECLASSIFICAR (Art. 74º / Art. 75º — "até resolução ou
    #    reclassificação")
    # ==========================================================

    def reclassify(self, conflict_id: str) -> Dict[str, Any]:
        """Recalcula a severidade de um conflito ativo a partir das evidências atuais."""
        conflict = self._get_conflict(conflict_id)

        if conflict["status"] != "ATIVO":
            raise ValueError(f"Conflito {conflict_id} não está ativo")

        conflict["level"] = self._classify_severity(
            conflict["iec_a_id"], conflict["iec_b_id"]
        )

        return conflict

    # ==========================================================
    # 4. RESOLVER (Art. 76º / Art. 77º)
    # ==========================================================

    def resolve_conflict(
        self,
        conflict_id: str,
        mechanism: str,
        outcome: str,
        note: str,
    ) -> Dict[str, Any]:
        """
        Resolve um conflito ativo.

        mechanism: um de RESOLUTION_MECHANISMS (Art. 76º).
        outcome: um de RESOLUTION_OUTCOMES (Art. 77º) --
        "resolvido por integração" ou "resolvido por refutação".

        O conflito nunca é apagado (Art. 77º) -- só marcado.
        """
        if mechanism not in RESOLUTION_MECHANISMS:
            raise ValueError(f"Mecanismo inválido: {mechanism}")
        if outcome not in RESOLUTION_OUTCOMES:
            raise ValueError(f"Desfecho inválido: {outcome}")

        conflict = self._get_conflict(conflict_id)

        if conflict["status"] != "ATIVO":
            raise ValueError(f"Conflito {conflict_id} não está ativo")

        conflict["status"] = "RESOLVIDO"
        conflict["resolution"] = {
            "mechanism": mechanism,
            "outcome": outcome,
            "note": note,
        }
        conflict["resolved_at"] = datetime.now(UTC).isoformat()

        return conflict

    # ==========================================================
    # 5. CONSULTAS
    # ==========================================================

    def _get_conflict(self, conflict_id: str) -> Dict[str, Any]:
        if conflict_id not in self.conflicts:
            raise ValueError(f"Conflito {conflict_id} não registrado")
        return self.conflicts[conflict_id]

    def get_conflict(self, conflict_id: str) -> Dict[str, Any]:
        """Retorna um conflito pelo id."""
        return self._get_conflict(conflict_id)

    def list_active_conflicts(self) -> List[Dict[str, Any]]:
        """Lista conflitos ainda ativos (Art. 75º: permanecem ativos até resolução)."""
        return [c for c in self.conflicts.values() if c["status"] == "ATIVO"]

    def list_conflicts_for_iec(self, iec_id: str) -> List[Dict[str, Any]]:
        """Lista todos os conflitos (ativos ou resolvidos) envolvendo uma IEC."""
        return [
            c for c in self.conflicts.values()
            if c["iec_a_id"] == iec_id or c["iec_b_id"] == iec_id
        ]

    def stats(self) -> Dict[str, Any]:
        """Estatísticas dos conflitos registrados."""
        active = self.list_active_conflicts()
        by_level = {level: 0 for level in CONFLICT_LEVELS}
        for c in active:
            by_level[c["level"]] += 1

        return {
            "total_conflicts": len(self.conflicts),
            "active_conflicts": len(active),
            "resolved_conflicts": len(self.conflicts) - len(active),
            "active_by_level": by_level,
        }

    def __repr__(self) -> str:
        return f"ConflictSolver(conflicts={len(self.conflicts)})"
