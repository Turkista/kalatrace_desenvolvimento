from typing import Dict, Any, List
from datetime import datetime, UTC

from engines.research_strategy.research_strategy_engine import ResearchStrategyEngine
from consensus.consensus_engine import ConsensusEngine
from dynamic.strategy_adapter import StrategyAdapter


class DynamicEngine:
    """
    Dynamic

    "Dynamic representa a capacidade de adaptação estratégica do
    KALATRACE... permitir que o sistema ajuste estratégias,
    prioridades e comportamentos de acordo com mudanças no
    ambiente de conhecimento." (dynamic/README.md)

    Terceiro e último módulo novo da FASE 5 (PROPOSTA -- roadmap
    de estabilização, sessão de 09/08/2026). README lista
    "StarHouse, Prediction, Simulation, Consensus, Metacognition"
    como fontes -- StarHouse, Prediction e Simulation não existem
    no projeto hoje; Metacognition existe (metacognition/) mas
    observa o ciclo de inferência do grafo, não produz sinal
    estratégico consumível por Dynamic ainda. Esta implementação
    usa apenas o que é real e já combinado com o usuário: o plano
    ranqueado do Research Strategy Engine (RSE) + os sinais de
    controvérsia do Consensus.

    Fachada que compõe:
    - strategy_adapter.py (StrategyAdapter): aplica o ajuste sobre
      o plano do RSE.

    Limitação (README): "Dynamic não cria conhecimento científico...
    sua função é adaptar a estratégia de funcionamento do sistema."
    Esta implementação não altera o RSE nem o Consensus -- lê os
    dois, produz um plano adaptado à parte, e mantém histórico
    (nenhum plano adaptado é apagado, mesmo princípio geral do
    DOCUMENTO 30 já usado nos outros módulos).
    """

    def __init__(self, strategy_engine: ResearchStrategyEngine, consensus_engine: ConsensusEngine):
        self.strategy_engine = strategy_engine
        self.consensus_engine = consensus_engine
        self.adapter = StrategyAdapter()

        self.adapted_plans: List[Dict[str, Any]] = []

    # ==========================================================
    # ADAPTAR ESTRATÉGIA (a partir do plano atual do RSE)
    # ==========================================================

    def adapt_strategy(self) -> Dict[str, Any]:
        """
        Constrói o plano estratégico atual do RSE e o adapta com
        os sinais de controvérsia do Consensus. Se nenhuma
        oportunidade foi avaliada ainda, o RSE devolve um plano
        com ranked_opportunities vazio (não levanta erro -- ver
        ResearchPlanner.build_plan) e este método adapta esse
        plano vazio normalmente.
        """
        plan = self.strategy_engine.build_strategic_plan()
        controversial = self.consensus_engine.controversial_iecs()

        adapted = self.adapter.adapt(plan, controversial)
        shift = self._detect_priority_shift(adapted)

        record = {
            "adapted_plan": adapted,
            "controversial_iecs_considered": controversial,
            "priority_shift": shift,
            "recorded_at": datetime.now(UTC).isoformat(),
        }
        self.adapted_plans.append(record)

        return record

    # ==========================================================
    # DETECÇÃO DE MUDANÇA DE PRIORIDADE (Art. 6º do RSE, aplicado ao adaptado)
    # ==========================================================

    def _detect_priority_shift(self, adapted_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara o topo do plano adaptado atual com o do plano
        adaptado anterior (se existir). Precisa de ao menos um
        plano adaptado anterior -- com 0, não há o que comparar.
        """
        if not self.adapted_plans:
            return None

        previous_top = self.adapted_plans[-1]["adapted_plan"]["ranked_opportunities"]
        current_top = adapted_plan["ranked_opportunities"]

        if not previous_top or not current_top:
            return None

        if previous_top[0]["iec_id"] == current_top[0]["iec_id"]:
            return None

        return {
            "from_iec_id": previous_top[0]["iec_id"],
            "to_iec_id": current_top[0]["iec_id"],
        }

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_current_adapted_plan(self) -> Dict[str, Any]:
        if not self.adapted_plans:
            raise ValueError("Nenhum plano adaptado gerado ainda")
        return self.adapted_plans[-1]

    def get_adapted_plan_history(self) -> List[Dict[str, Any]]:
        return self.adapted_plans

    def stats(self) -> Dict[str, Any]:
        return {
            "adapted_plans_generated": len(self.adapted_plans),
        }

    def __repr__(self) -> str:
        return f"DynamicEngine(adapted_plans={len(self.adapted_plans)})"
