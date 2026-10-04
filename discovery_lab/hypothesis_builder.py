from typing import Dict, Any, List


class HypothesisBuilder:
    """
    Hypothesis Builder

    Organiza lacunas científicas (CuriosityEngine.analyze_gap) e
    conexões do grafo em candidatos a hipótese estruturados --
    "transformar conexões, padrões e observações em hipóteses
    estruturadas que possam ser posteriormente analisadas,
    simuladas e validadas" (discovery_lab/README.md).

    Escopo honesto (mesmo princípio já usado em
    ContextBuilder para a SCR 15.8 "novas hipóteses" e em
    StrategyGenerator para o DOCUMENTO 25): este módulo NÃO
    escreve o texto de uma hipótese científica -- isso exigiria
    raciocínio combinatório/gerativo sobre o conteúdo das IECs,
    capacidade que o projeto não tem (mesma limitação documentada
    em engines/scientific_context/context_builder.py). O que ele
    faz é preparar e classificar candidatos -- "organização de
    possibilidades emergentes; preparação de hipóteses para
    investigação" (README) -- prontos para receber, no futuro, um
    agente de IA real que redija o texto (ver agents/research_agent.py,
    que hoje também só empacota o Engine, não gera texto).

    Classificação de cada candidato:
    - GAP_ISOLADO: lacuna de conhecimento sem nenhuma conexão
      inferida no grafo -- território inexplorado, sem apoio de
      conhecimento vizinho.
    - GAP_CONECTADO: lacuna com uma ou mais IECs conectadas --
      candidato a hipótese por combinação (README: "combinação de
      conhecimentos existentes").
    """

    # curiosity_level (CuriosityEngine) que justifica virar candidato --
    # abaixo disso, a lacuna existe mas não é prioritária o bastante
    # para virar candidato de hipótese agora.
    QUALIFYING_LEVELS = {"CRITICAL", "HIGH", "MEDIUM"}

    def build_candidate(
        self,
        iec_id: str,
        statement: str,
        gap: Dict[str, Any],
        questions: List[str],
        connected_iec_ids: List[str],
    ) -> Dict[str, Any]:
        """Constrói um candidato a hipótese estruturado para uma IEC, a partir de uma lacuna já analisada."""
        qualifies = gap["curiosity_level"] in self.QUALIFYING_LEVELS
        exploration_type = "GAP_CONECTADO" if connected_iec_ids else "GAP_ISOLADO"

        return {
            "iec_id": iec_id,
            "statement": statement,
            "curiosity_level": gap["curiosity_level"],
            "qualifies_as_candidate": qualifies,
            "exploration_type": exploration_type,
            "connected_iec_ids": connected_iec_ids,
            "research_questions": questions,
            "hypothesis_text": None,
            "not_determinable": {
                "hypothesis_text": (
                    "Geração de texto de hipótese exigiria raciocínio combinatório/"
                    "gerativo sobre o conteúdo das IECs -- não implementado (mesma "
                    "limitação da SCR, Seção 15.8, e de todos os agentes de "
                    "agents/, que também não chamam um LLM real)."
                ),
            },
        }

    def __repr__(self) -> str:
        return "HypothesisBuilder()"
