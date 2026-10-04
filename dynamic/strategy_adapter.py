from typing import Dict, Any, List


class StrategyAdapter:
    """
    Strategy Adapter

    Ajusta o plano estratégico já ranqueado pelo Research Strategy
    Engine (RSE) usando sinais do Consensus -- "permitir que o
    sistema ajuste estratégias, prioridades e comportamentos de
    acordo com mudanças no ambiente de conhecimento" (dynamic/README.md).

    Não recalcula o composite_score do RSE (isso é
    engines/research_strategy/prioritizer.py) -- aplica um ajuste
    documentado por cima do ranking já existente, e registra o
    motivo de cada ajuste (nunca reordena silenciosamente).

    Regra de ajuste desta implementação (interpretação; o
    DOCUMENTO 25/README não especifica o algoritmo, só o
    princípio de "adaptação estratégica"): oportunidades cuja IEC
    está classificada como CONTROVERSIA pelo Consensus sobem de
    posição no plano adaptado -- controvérsia é, por definição, um
    sinal de que mais investigação é valiosa agora, mesmo que o
    composite_score original não capture isso (o Prioritizer não
    consulta o Consensus). Sujeita a calibração futura.
    """

    # quanto uma oportunidade controversa sobe no ranking adaptado,
    # em pontos de composite_score equivalente -- interpretação
    # desta implementação, ver docstring da classe.
    CONTROVERSY_BOOST = 0.15

    def adapt(self, plan: Dict[str, Any], controversial_iec_ids: List[str]) -> Dict[str, Any]:
        """
        Recebe um plano já ranqueado (ResearchPlanner.build_plan)
        e a lista de IECs controversas (ConsensusEngine.controversial_iecs)
        e devolve um plano adaptado, reordenado quando aplicável.
        """
        adjusted = []
        for opportunity in plan["ranked_opportunities"]:
            iec_id = opportunity["iec_id"]
            base_score = opportunity["priority"]["composite_score"]
            is_controversial = iec_id in controversial_iec_ids

            adjusted_score = round(base_score + self.CONTROVERSY_BOOST, 3) if is_controversial else base_score

            adjusted.append({
                **opportunity,
                "adjusted_score": adjusted_score,
                "strategy_adjustment": "CONTROVERSIA_PRIORIZADA" if is_controversial else "MANTIDA",
                "adjustment_reason": (
                    f"Consensus classificou esta IEC como CONTROVERSIA -- prioridade "
                    f"elevada em +{self.CONTROVERSY_BOOST} sobre o composite_score original."
                    if is_controversial else
                    "Nenhum sinal do Consensus altera a prioridade original do RSE."
                ),
            })

        adjusted.sort(key=lambda o: o["adjusted_score"], reverse=True)

        return {
            "plan_id": plan["plan_id"],
            "ranked_opportunities": adjusted,
            "adapted_at": plan["generated_at"],
        }

    def __repr__(self) -> str:
        return "StrategyAdapter()"
