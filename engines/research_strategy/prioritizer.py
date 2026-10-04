from typing import Dict, Any, List

from contracts.iec_contract import IECContract
from storage.evidence_store import EvidenceStore
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine


class Prioritizer:
    """
    Prioritizer

    Calcula o valor estratégico de uma oportunidade científica
    (DOCUMENTO 25 -- Research Strategy Engine, Art. 3º: "Nem
    toda lacuna científica possui o mesmo valor estratégico").

    Escopo honesto desta implementação -- dos 8 critérios do
    Art. 5º, 4 são computáveis com os dados e módulos que já
    existem no projeto; os outros 4 exigem informação que o
    projeto não modela hoje (recursos disponíveis, relevância
    clínica julgada por humano, potencial de aplicação
    tecnológica, existência de outros "projetos" no sistema --
    não há conceito de Project implementado):

    Computáveis:
    - "Impacto Científico" -> proxy: nº de IECs conectadas a
      esta no grafo (quanto mais conectada, mais conhecimento
      depende, direta ou indiretamente, dela).
    - "Originalidade" -> proxy: inverso da quantidade de
      evidência já existente (0 evidências = território
      inexplorado; muita evidência = confirmação adicional).
    - "Nível de Evidência Atual" -> direto do
      KnowledgeEvolutionEngine (estado + força de evidência).
    - "Urgência Científica" -> direto do CuriosityEngine
      (curiosity_level).

    Não computáveis (retornados como null, motivo explícito):
    - "Viabilidade Experimental", "Relevância Clínica",
      "Potencial Translacional", "Sinergia com Projetos
      Ativos".

    Os 4 proxies acima e a fórmula de agregação (média simples,
    ver _composite_score) são interpretação desta implementação
    -- o DOCUMENTO 25 nomeia os critérios, não especifica como
    computá-los nem como combiná-los. Sujeitos a calibração
    futura, principalmente se o projeto vier a modelar
    "projetos" e recursos experimentais formalmente.
    """

    NOT_DETERMINABLE_CRITERIA = {
        "viabilidade_experimental": (
            "Exigiria modelagem de recursos experimentais disponíveis -- não "
            "implementada no projeto."
        ),
        "relevancia_clinica": (
            "Exigiria julgamento clínico humano ou uma ontologia clínica ligada "
            "às IECs -- não implementada (ver engines/scientific_context/ontology_mapper.py)."
        ),
        "potencial_translacional": (
            "Exigiria avaliação de aplicabilidade tecnológica/terapêutica/industrial -- "
            "fora do escopo de dados que o projeto modela hoje."
        ),
        "sinergia_com_projetos_ativos": (
            "Exigiria um conceito de \"Project\" formalizado no projeto -- não "
            "implementado (ver DOCUMENTO 72, entidade Project, ainda sem módulo)."
        ),
    }

    def __init__(
        self,
        graph,
        evidence_store: EvidenceStore,
        evolution_engine: KnowledgeEvolutionEngine,
        curiosity_engine: CuriosityEngine,
    ):
        self.graph = graph
        self.evidence_store = evidence_store
        self.evolution_engine = evolution_engine
        self.curiosity_engine = curiosity_engine

    # ==========================================================
    # PONTUAR UMA OPORTUNIDADE (Art. 5º)
    # ==========================================================

    def score(self, iec_id: str) -> Dict[str, Any]:
        """Pontua uma oportunidade científica nos critérios computáveis do Art. 5º."""

        state = self.evolution_engine.get_state(iec_id)
        evidence_count = len(self.evidence_store.get_evidence_for_iec(iec_id))
        evidence_strength = self.evidence_store.compute_evidence_strength(iec_id)

        connected_count = len(self.graph.edges_of(iec_id)) if hasattr(self.graph, "edges_of") else 0

        scientific_impact = min(1.0, connected_count / 5.0)
        originality = 1.0 - min(1.0, evidence_count / 5.0)
        evidence_level = evidence_strength
        urgency = self._urgency_from_curiosity(iec_id)

        composite = self._composite_score(scientific_impact, originality, evidence_level, urgency)

        return {
            "iec_id": iec_id,
            "criteria": {
                "impacto_cientifico": round(scientific_impact, 3),
                "originalidade": round(originality, 3),
                "nivel_de_evidencia_atual": round(evidence_level, 3),
                "urgencia_cientifica": round(urgency, 3),
            },
            "not_determinable": dict(self.NOT_DETERMINABLE_CRITERIA),
            "composite_score": round(composite, 3),
            "epistemic_state": state["current_state"],
        }

    # ==========================================================
    # URGÊNCIA (a partir do CuriosityEngine, API pública)
    # ==========================================================

    def _urgency_from_curiosity(self, iec_id: str) -> float:
        levels = {"CRITICAL": 1.0, "HIGH": 0.75, "MEDIUM": 0.5, "LOW": 0.25, "MINIMAL": 0.0}
        state = self.evolution_engine.get_state(iec_id)
        contract = IECContract(
            iec_id=iec_id,
            title=state["statement"][:40],
            statement=state["statement"],
            knowledge_type="Conhecimento",
        )
        gap = self.curiosity_engine.analyze_gap(contract)
        return levels.get(gap["curiosity_level"], 0.0)

    # ==========================================================
    # AGREGAÇÃO (ver nota de escopo no docstring da classe)
    # ==========================================================

    def _composite_score(self, impact: float, originality: float, evidence_level: float, urgency: float) -> float:
        return (impact + originality + evidence_level + urgency) / 4.0

    def __repr__(self) -> str:
        return "Prioritizer()"
