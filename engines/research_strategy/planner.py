from typing import Dict, Any, List
from datetime import datetime, UTC


class ResearchPlanner:
    """
    Research Planner

    Mantém o plano estratégico de pesquisa (DOCUMENTO 25, Art.
    6º, "Estratégia Adaptativa": "o planejamento produzido pelo
    RSE nunca será definitivo. Sempre que o estado do
    conhecimento evoluir, as prioridades poderão ser
    reorganizadas").

    Não pontua nem recomenda (isso é Prioritizer/
    StrategyGenerator) -- organiza as oportunidades já avaliadas
    em um plano ranqueado e mantém o histórico de planos
    (nenhum apagado, mesmo princípio geral do DOCUMENTO 30).
    """

    def __init__(self):
        self.plans: List[Dict[str, Any]] = []

    # ==========================================================
    # CONSTRUIR PLANO (Art. 6º)
    # ==========================================================

    def build_plan(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Constrói um plano estratégico a partir de oportunidades
        já avaliadas (score + recomendação), ranqueadas por
        composite_score (do Prioritizer).
        """
        ranked = sorted(opportunities, key=lambda o: o["priority"]["composite_score"], reverse=True)

        plan = {
            "plan_id": f"PLAN-{len(self.plans) + 1}",
            "ranked_opportunities": ranked,
            "generated_at": datetime.now(UTC).isoformat(),
        }
        self.plans.append(plan)

        return plan

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_current_plan(self) -> Dict[str, Any]:
        """Retorna o plano mais recente."""
        if not self.plans:
            raise ValueError("Nenhum plano gerado ainda")
        return self.plans[-1]

    def get_plan_history(self) -> List[Dict[str, Any]]:
        """Retorna todos os planos já gerados (Art. 6º: nenhum é definitivo)."""
        return self.plans

    def __repr__(self) -> str:
        return f"ResearchPlanner(plans={len(self.plans)})"
