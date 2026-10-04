from typing import Dict, Any, List

from storage.evidence_store import EvidenceStore


class StrategyGenerator:
    """
    Strategy Generator

    Gera uma recomendação de próximo passo para uma oportunidade
    científica, a partir das 8 recomendações oficiais do
    DOCUMENTO 25 (Art. 7º):

        fortalecer determinada hipótese; produzir novos
        experimentos in vitro; avançar para estudos in vivo;
        realizar estudos mecanísticos adicionais; ampliar o
        número de amostras; buscar colaboração
        multidisciplinar; iniciar revisão sistemática; aguardar
        novas evidências antes de prosseguir.

    "Todas as recomendações deverão apresentar sua justificativa
    científica" (Art. 7º) e têm "caráter consultivo... a decisão
    final permanece sob responsabilidade do pesquisador" (Art.
    9º) -- a saída desta classe é sempre uma sugestão com
    justificativa, nunca uma instrução.

    Escopo honesto: a árvore de decisão abaixo (qual das 8
    recomendações escolher, e em que ordem verificar as
    condições) é interpretação desta implementação -- o
    DOCUMENTO 25 lista as recomendações possíveis, não o
    algoritmo de seleção entre elas. "Buscar colaboração
    multidisciplinar" nunca é escolhida automaticamente aqui: é
    uma decisão que depende de contexto organizacional (quem
    está disponível, que parcerias existem) que o projeto não
    modela -- retornada apenas como alternativa possível no
    campo "alternativas", nunca como recomendação principal.
    """

    def __init__(self, evidence_store: EvidenceStore):
        self.evidence_store = evidence_store

    # ==========================================================
    # GERAR RECOMENDAÇÃO (Art. 7º)
    # ==========================================================

    def generate(self, iec_id: str, epistemic_state: str, scr_panorama: Dict[str, Any]) -> Dict[str, Any]:
        """Gera a recomendação de próximo passo, com justificativa, para uma oportunidade."""

        evidences = self.evidence_store.get_evidence_for_iec(iec_id)
        evidence_count = len(evidences)
        types = {e.evidence_type for e in evidences}
        has_divergence = bool(scr_panorama.get("divergent_evidence"))

        if evidence_count == 0:
            recommendation = "PRODUZIR_NOVOS_EXPERIMENTOS_IN_VITRO"
            justification = "Nenhuma evidência vinculada ainda -- território a explorar desde o início."

        elif has_divergence:
            recommendation = "REALIZAR_ESTUDOS_MECANISTICOS_ADICIONAIS"
            justification = (
                f"{len(scr_panorama['divergent_evidence'])} divergência(s) registrada(s) "
                "com outras IECs -- entender o mecanismo pode explicar a discrepância."
            )

        elif evidence_count <= 2:
            recommendation = "AMPLIAR_NUMERO_DE_AMOSTRAS"
            justification = f"Só {evidence_count} evidência(s) vinculada(s) -- sustentação ainda frágil."

        elif types == {"in_vitro"}:
            recommendation = "AVANCAR_PARA_ESTUDOS_IN_VIVO"
            justification = "Toda a evidência disponível é in vitro -- próximo nível de validação é modelo animal."

        elif epistemic_state in ("QUESTIONED", "NEEDS_REVIEW"):
            recommendation = "FORTALECER_HIPOTESE"
            justification = f"Estado epistemológico atual ({epistemic_state}) indica sustentação enfraquecendo."

        elif scr_panorama.get("scientific_consensus") == "CONTROVERSIA":
            recommendation = "INICIAR_REVISAO_SISTEMATICA"
            justification = "Consenso científico indica controvérsia -- uma revisão sistemática organizaria o que já existe."

        else:
            recommendation = "AGUARDAR_NOVAS_EVIDENCIAS"
            justification = "Nenhuma condição das demais recomendações se aplica no momento."

        return {
            "iec_id": iec_id,
            "recommendation": recommendation,
            "justification": justification,
            "alternatives": ["BUSCAR_COLABORACAO_MULTIDISCIPLINAR"],
            "advisory_note": (
                "Recomendação de caráter consultivo (DOCUMENTO 25, Art. 9º) -- "
                "a decisão final permanece com o pesquisador."
            ),
        }

    def __repr__(self) -> str:
        return "StrategyGenerator()"
