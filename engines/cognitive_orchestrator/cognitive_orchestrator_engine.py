from typing import Dict, Any, List

from acquisition.manual_acquisition import ManualAcquisition
from engines.base.base_engine import CoreEngine
from graph.knowledge_graph import KnowledgeGraph
from validation.validation_engine import ValidationEngine
from validation.ontology_validator import OntologyValidator
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_research.scientific_research_engine import ScientificResearchEngine
from engines.scientific_context.scientific_context_engine import ScientificContextEngine
from engines.research_strategy.research_strategy_engine import ResearchStrategyEngine
from storage.evidence_store import EvidenceStore
from engines.cognitive_orchestrator.coordinator import CycleCoordinator
from engines.cognitive_orchestrator.pipeline import CyclePipeline
from engines.cognitive_orchestrator.workflow import CYCLE_STEPS, COGNITIVE_STATES
from consensus.consensus_engine import ConsensusEngine
from discovery_lab.discovery_lab_engine import DiscoveryLabEngine
from dynamic.dynamic_engine import DynamicEngine
from parsi import PARSIEngine
from starhouse import StarHouseEngine
from horse import HorseEngine
from prediction import PredictionEngine
from simulation import SimulationEngine, SimulationChange


class CognitiveOrchestrator:
    """
    Cognitive Orchestrator (CO)

    Coordenador de todos os processos cognitivos do KALATRACE
    (DOCUMENTO 26): inicia ciclos científicos, define a ordem
    de execução dos módulos, monitora o estado de cada
    investigação, registra o histórico completo das execuções
    e garante consistência entre os componentes.

    "O CO não interpreta resultados experimentais. Ele
    coordena os processos que permitem essa interpretação."
    (Art. 10º)

    Implementado (roadmap de estabilização, sessão de
    08/08/2026) depois que os módulos individuais que ele
    coordena (ManualAcquisition, KnowledgeEvolutionEngine,
    CuriosityEngine, ScientificResearchEngine, ValidationEngine)
    já existiam, mas eram ligados manualmente dentro de run.py/
    app.py, editados a cada novo módulo -- exatamente o problema
    que o Art. 7º descreve: "Os módulos do KALATRACE não deverão
    depender diretamente uns dos outros. Toda comunicação
    ocorrerá por intermédio do Cognitive Orchestrator."

    Fachada pública que compõe:
    - workflow.py: definição estática do ciclo e dos estados
      (Art. 5º/6º);
    - coordinator.py (CycleCoordinator): estado e histórico por
      ciclo (Art. 6º/9º);
    - pipeline.py (CyclePipeline): execução real dos passos
      contra os engines existentes.

    Nota importante: os 3 passos do ciclo oficial que faltavam
    (Scientific Context Reconstruction e Research Strategy Engine)
    foram implementados na mesma sessão (08/08/2026) e já fazem
    parte do ciclo -- engines/scientific_context/ e
    engines/research_strategy/. Ver workflow.py para a lista
    completa do que está implementado.

    FASE 5 (PROPOSTA) -- Consensus, Discovery Lab e Dynamic
    (sessão de 09/08/2026): os 3 primeiros módulos da Camada
    Cognitiva Avançada proposta (ver READMEs em consensus/,
    discovery_lab/, dynamic/) também são coordenados aqui, mas
    NÃO fazem parte do ciclo oficial do DOCUMENTO 26 (Art. 5º) --
    workflow.py CYCLE_STEPS continua descrevendo só os 10 passos
    desse documento. Consensus/Discovery Lab/Dynamic são expostos
    como métodos consultivos (track_consensus, generate_hypothesis,
    adapt_strategy), chamados dentro de CyclePipeline.run() sempre
    que o dado de que dependem já existe naquele ponto do ciclo
    (panorama da SCR para Consensus; lacuna do CuriosityEngine
    para Discovery Lab) -- nunca fabricando um passo do Art. 5º
    que não existe. adapt_strategy() fica de fora do run() (como
    build_strategic_plan já era) porque compara plano atual com o
    anterior -- não faz sentido chamá-lo isoladamente por IEC.
    """

    def __init__(self, evidence_store: EvidenceStore = None, graph: KnowledgeGraph = None):
        self.evidence_store = evidence_store or EvidenceStore()
        self.graph = graph or KnowledgeGraph()

        self.acquisition = ManualAcquisition()
        self.core_engine = CoreEngine()
        self.validation_engine = ValidationEngine(self.graph, self.evidence_store)
        self.ontology_validator = OntologyValidator()
        self.evolution_engine = KnowledgeEvolutionEngine(self.evidence_store)
        self.curiosity_engine = CuriosityEngine(self.evidence_store)
        self.research_engine = ScientificResearchEngine(self.evidence_store)
        self.context_engine = ScientificContextEngine(
            self.evidence_store, self.evolution_engine, self.curiosity_engine
        )
        self.strategy_engine = ResearchStrategyEngine(
            self.graph, self.evidence_store, self.evolution_engine,
            self.curiosity_engine, self.context_engine,
        )

        # FASE 5 (PROPOSTA) -- sessão de 09/08/2026 (ver docstring da classe)
        self.consensus_engine = ConsensusEngine()
        self.discovery_lab_engine = DiscoveryLabEngine(
            self.evidence_store, self.evolution_engine, self.curiosity_engine,
        )
        self.dynamic_engine = DynamicEngine(self.strategy_engine, self.consensus_engine)
        self.parsi_engine = PARSIEngine()
        self.starhouse_engine = StarHouseEngine(self.graph)
        self.horse_engine = HorseEngine(self.graph)
        self.prediction_engine = PredictionEngine(self.graph)
        self.simulation_engine = SimulationEngine(self.graph)

        self.coordinator = CycleCoordinator()
        self.pipeline = CyclePipeline(
            graph=self.graph,
            evidence_store=self.evidence_store,
            acquisition=self.acquisition,
            core_engine=self.core_engine,
            validation_engine=self.validation_engine,
            evolution_engine=self.evolution_engine,
            curiosity_engine=self.curiosity_engine,
            research_engine=self.research_engine,
            context_engine=self.context_engine,
            strategy_engine=self.strategy_engine,
            coordinator=self.coordinator,
            parsi_engine=self.parsi_engine,
            consensus_engine=self.consensus_engine,
            discovery_lab_engine=self.discovery_lab_engine,
            ontology_validator=self.ontology_validator,
        )

    # ==========================================================
    # 1. INICIAR CICLO (Art. 5º -- evento: nova submissão manual)
    # ==========================================================

    def run_cycle(
        self,
        statement: str,
        submitted_by: str,
        submission_type: str = "observacao",
        inference_threshold: float = 0.55,
    ) -> Dict[str, Any]:
        """
        Executa o ciclo cognitivo completo para uma submissão
        nova (Art. 8º, evento "nova IEC").
        """
        return self.pipeline.run(
            statement=statement,
            submitted_by=submitted_by,
            submission_type=submission_type,
            inference_threshold=inference_threshold,
        )

    # ==========================================================
    # 2. CONSULTAS
    # ==========================================================

    def observe_knowledge_map(self) -> Dict[str, Any]:
        """Observe the current knowledge graph through StarHouse.

        This consultative operation is intentionally outside the official
        cognitive cycle. The Cognitive Orchestrator remains the communication
        boundary for the module.
        """
        return self.starhouse_engine.observe().to_dict()

    def explore_knowledge(
        self,
        seeds=None,
        statement: str = None,
        max_hops: int = 3,
        max_paths: int = 8,
    ) -> Dict[str, Any]:
        """Explore non-linear knowledge paths through the Horse specialist."""
        parsi_result = self.parsi_engine.interpret(statement) if statement else None
        starhouse_map = self.starhouse_engine.observe()
        return self.horse_engine.explore(
            seeds=seeds, parsi_result=parsi_result,
            starhouse_map=starhouse_map, max_hops=max_hops, max_paths=max_paths
        ).to_dict()

    def predict_knowledge(
        self,
        target_id: str = None,
        statement: str = None,
        horizon: str = "medium_term",
        max_scenarios: int = 3,
    ) -> Dict[str, Any]:
        """Project probabilistic scenarios using PARSI, StarHouse and Horse signals."""
        parsi_result = self.parsi_engine.interpret(statement) if statement else None
        starhouse_map = self.starhouse_engine.observe()
        horse_result = self.horse_engine.explore(
            seeds=[target_id] if target_id else None,
            parsi_result=parsi_result,
            starhouse_map=starhouse_map,
        )
        return self.prediction_engine.predict(
            target_id=target_id, statement=statement, parsi_result=parsi_result,
            starhouse_map=starhouse_map, horse_exploration=horse_result,
            horizon=horizon, max_scenarios=max_scenarios,
        ).to_dict()

    def simulate_knowledge(
        self,
        title: str = "Virtual experiment",
        changes=None,
        target_id: str = None,
        statement: str = None,
        horizon: str = "medium_term",
        alternatives: int = 3,
    ) -> Dict[str, Any]:
        """Run isolated hypothetical experiments without mutating official knowledge."""
        parsi_result = self.parsi_engine.interpret(statement) if statement else None
        starhouse_map = self.starhouse_engine.observe()
        horse_result = self.horse_engine.explore(
            seeds=[target_id] if target_id else None, parsi_result=parsi_result,
            starhouse_map=starhouse_map,
        )
        prediction_result = self.prediction_engine.predict(
            target_id=target_id, statement=statement, parsi_result=parsi_result,
            starhouse_map=starhouse_map, horse_exploration=horse_result,
            horizon=horizon,
        )
        return self.simulation_engine.simulate(
            title=title, changes=changes, prediction=prediction_result,
            horse_exploration=horse_result, starhouse_map=starhouse_map,
            alternatives=alternatives,
        ).to_dict()

    def get_cycle_state(self, iec_id: str) -> Dict[str, Any]:
        """Retorna o ciclo completo (estado + histórico) de uma IEC."""
        return self.coordinator.get_cycle(iec_id)

    def list_active_cycles(self) -> List[Dict[str, Any]]:
        """Lista ciclos ainda ativos (Art. 5º: aguardando novas evidências)."""
        return self.coordinator.list_active_cycles()

    def state_distribution(self) -> Dict[str, int]:
        """Conta ciclos por estado cognitivo (Art. 6º)."""
        return self.coordinator.state_distribution()

    def workflow_definition(self) -> Dict[str, Any]:
        """Retorna a definição oficial do ciclo e dos estados (Art. 5º/6º)."""
        return {
            "cycle_steps": CYCLE_STEPS,
            "cognitive_states": COGNITIVE_STATES,
        }

    def build_strategic_plan(self) -> Dict[str, Any]:
        """
        Constrói o plano estratégico ranqueado (DOCUMENTO 25, Art.
        6º) a partir de todas as oportunidades já avaliadas nos
        ciclos executados até agora.
        """
        return self.strategy_engine.build_strategic_plan()

    def adapt_strategy(self) -> Dict[str, Any]:
        """
        FASE 5 (PROPOSTA) -- Dynamic: adapta o plano estratégico
        atual do RSE com os sinais de controvérsia já observados
        pelo Consensus. Fora do run_cycle() de propósito (ver
        docstring da classe) -- compara com o plano adaptado
        anterior, não faz sentido rodar por IEC isolada.
        """
        return self.dynamic_engine.adapt_strategy()

    # ==========================================================
    # 3. ESTATÍSTICAS E SAÚDE
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Métricas agregadas do Cognitive Orchestrator."""
        return {
            "total_cycles": len(self.coordinator.cycles),
            "active_cycles": len(self.list_active_cycles()),
            "state_distribution": self.state_distribution(),
            "graph_nodes": len(self.graph.nodes),
            "acquisition": self.acquisition.stats(),
            "evolution": self.evolution_engine.stats(),
            "curiosity": self.curiosity_engine.stats(),
            "research": self.research_engine.stats(),
            "context": self.context_engine.stats(),
            "strategy": self.strategy_engine.stats(),
            "consensus": self.consensus_engine.stats(),
            "discovery_lab": self.discovery_lab_engine.stats(),
            "dynamic": self.dynamic_engine.stats(),
            "parsi": self.parsi_engine.stats(),
            "starhouse": self.starhouse_engine.stats(),
            "horse": self.horse_engine.stats(),
            "prediction": self.prediction_engine.stats(),
            "simulation": self.simulation_engine.stats(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Verifica se todos os módulos coordenados estão íntegros."""
        return {
            "cognitive_orchestrator": "OK",
            "graph_connected": self.graph is not None,
            "evidence_store_connected": self.evidence_store is not None,
            "modules": {
                "acquisition": self.acquisition is not None,
                "validation_engine": self.validation_engine is not None,
                "evolution_engine": self.evolution_engine.health_check(),
                "curiosity_engine": self.curiosity_engine is not None,
                "research_engine": self.research_engine is not None,
                "context_engine": self.context_engine is not None,
                "strategy_engine": self.strategy_engine is not None,
                "consensus_engine": self.consensus_engine is not None,
                "discovery_lab_engine": self.discovery_lab_engine is not None,
                "dynamic_engine": self.dynamic_engine is not None,
                "parsi_engine": self.parsi_engine is not None,
            "starhouse_engine": self.starhouse_engine is not None,
            "prediction_engine": self.prediction_engine is not None,
            },
        }

    def __repr__(self) -> str:
        return (
            f"CognitiveOrchestrator("
            f"cycles={len(self.coordinator.cycles)}, "
            f"nodes={len(self.graph.nodes)}"
            f")"
        )
