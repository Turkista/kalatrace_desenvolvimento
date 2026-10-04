from typing import Dict, Any, Optional

from contracts.iec_contract import IECContract
from acquisition.manual_acquisition import ManualAcquisition
from engines.base.base_engine import CoreEngine
from graph.knowledge_graph import KnowledgeGraph
from inference.inference import infer
from validation.validation_engine import ValidationEngine
from validation.ontology_validator import OntologyValidator
from engines.knowledge_evolution.knowledge_evolution_engine import KnowledgeEvolutionEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_research.scientific_research_engine import ScientificResearchEngine
from engines.scientific_context.scientific_context_engine import ScientificContextEngine
from engines.research_strategy.research_strategy_engine import ResearchStrategyEngine
from storage.evidence_store import EvidenceStore
from engines.cognitive_orchestrator.coordinator import CycleCoordinator
from parsi import PARSIEngine


class CyclePipeline:
    """
    Cycle Pipeline

    Executa, na ordem real possível hoje (ver nota em
    workflow.py), os passos do ciclo cognitivo do DOCUMENTO 26
    contra os módulos que já existem no projeto -- registrando
    cada passo no CycleCoordinator (Art. 9º).

    Não decide o CICLO em si (isso é workflow.py, estático) nem
    guarda estado entre chamadas (isso é coordinator.py) -- só
    executa.

    Passos do Art. 5º sem módulo real (ex. futuras camadas de
    aquisição automatizada) seriam pulados com um passo
    "SKIPPED" registrado no histórico -- nunca silenciosamente
    ignorados. Hoje, todos os 8 passos executáveis do ciclo têm
    módulo real (Scientific Context Reconstruction e Research
    Strategy Engine, os dois últimos a faltar, implementados em
    08/08/2026) -- só ATUALIZACAO_DA_INTERFACE é NAO_APLICAVEL
    (projeto é só backend).

    consensus_engine/discovery_lab_engine (FASE 5 PROPOSTA, sessão
    de 09/08/2026): opcionais, de propósito -- não fazem parte do
    ciclo oficial do Art. 5º, então None é um valor válido (quem
    testa só o ciclo oficial não precisa deles). Quando presentes,
    são chamados nos pontos onde o dado de que dependem já existe
    (panorama da SCR; lacuna do CuriosityEngine), sem virar passo
    do coordinator -- ver comentários inline em run().
    """

    # threshold de prioridade do CuriosityEngine (1=CRITICAL,
    # 2=HIGH) que dispara o Scientific Research Engine -- mesmo
    # critério já usado em app.py (ver ENGINE-006/007, sessão de
    # 07/08/2026).
    SRE_TRIGGER_PRIORITY = 2

    def __init__(
        self,
        graph: KnowledgeGraph,
        evidence_store: EvidenceStore,
        acquisition: ManualAcquisition,
        core_engine: CoreEngine,
        validation_engine: ValidationEngine,
        evolution_engine: KnowledgeEvolutionEngine,
        curiosity_engine: CuriosityEngine,
        research_engine: ScientificResearchEngine,
        context_engine: ScientificContextEngine,
        strategy_engine: ResearchStrategyEngine,
        coordinator: CycleCoordinator,
        parsi_engine: PARSIEngine | None = None,
        consensus_engine=None,
        discovery_lab_engine=None,
        ontology_validator: OntologyValidator | None = None,
    ):
        self.graph = graph
        self.evidence_store = evidence_store
        self.acquisition = acquisition
        self.core_engine = core_engine
        self.validation_engine = validation_engine
        self.evolution_engine = evolution_engine
        self.curiosity_engine = curiosity_engine
        self.research_engine = research_engine
        self.context_engine = context_engine
        self.strategy_engine = strategy_engine
        self.coordinator = coordinator
        self.parsi_engine = parsi_engine
        # FASE 5 (PROPOSTA) -- opcionais: quem instanciar CyclePipeline
        # sem os módulos novos (ex. um teste isolado do ciclo oficial)
        # continua funcionando sem eles, sem quebrar.
        self.consensus_engine = consensus_engine
        self.discovery_lab_engine = discovery_lab_engine
        # Semantic validation is complementary and read-only. Keeping it
        # optional preserves the existing pipeline for isolated consumers.
        self.ontology_validator = ontology_validator

    # ==========================================================
    # CICLO COMPLETO PARA UMA SUBMISSÃO NOVA
    # ==========================================================

    def run(
        self,
        statement: str,
        submitted_by: str,
        submission_type: str = "observacao",
        inference_threshold: float = 0.55,
    ) -> Dict[str, Any]:
        """
        Executa o ciclo cognitivo completo (o que existe hoje)
        para uma submissão nova, do zero até o encerramento do
        ciclo ativo.
        """

        # PARSI — primeiro estágio cognitivo: interpreta a entrada antes
        # de ela virar uma IEC. A afirmação original permanece intacta;
        # a interpretação é anexada como metadado rastreável. PARSI não
        # faz parte dos passos epistemológicos do Art. 5º.
        parsi_result = None
        parsi_metadata = {}
        if self.parsi_engine is not None:
            parsi_result = self.parsi_engine.interpret(
                statement,
                source="CognitiveOrchestrator",
                metadata={"submitted_by": submitted_by, "submission_type": submission_type},
            )
            parsi_metadata = {
                "parsi": parsi_result.to_dict(),
            }

        # 1. AQUISICAO_DO_CONHECIMENTO
        capture = self.acquisition.capture(
            statement=statement,
            submitted_by=submitted_by,
            submission_type=submission_type,
        )
        iec = self.core_engine.create_iec(
            capture["capture_id"].replace("CAPTURE-", ""),
            statement,
            node_type=submission_type,
            metadata=parsi_metadata,
        )
        self.acquisition.mark_promoted(capture["capture_id"], iec_id=iec.id)
        self.graph.add_node(iec)

        contract = IECContract(
            iec_id=iec.id,
            title=statement[:40],
            statement=statement,
            knowledge_type=submission_type,
        )

        # Registro no Knowledge Evolution Engine adiantado para
        # UNKNOWN (sem avaliação de evidência ainda) -- necessário
        # porque SCIENTIFIC_CONTEXT_RECONSTRUCTION, abaixo, consulta
        # o estado da IEC (Art. 15.5) antes do passo
        # KNOWLEDGE_EVOLUTION_ENGINE (que aplica a avaliação real)
        # rodar.
        self.evolution_engine.register_iec(iec.to_contract())

        self.coordinator.start_cycle(iec.id, triggering_event="NOVA_SUBMISSAO_MANUAL")
        self.coordinator.record_step(
            iec_id=iec.id, step="AQUISICAO_DO_CONHECIMENTO", module="ManualAcquisition",
            inputs={"statement": statement, "submitted_by": submitted_by},
            outputs={"capture_id": capture["capture_id"], "iec_id": iec.id},
            justification="DOCUMENTO 23, Seção 8.1: captura íntegra da submissão do pesquisador.",
        )

        # 2. REASONING_ENGINE — adiantado em relação à ordem do Art. 5º
        # (ver nota em workflow.py): SCIENTIFIC_CONTEXT_RECONSTRUCTION,
        # logo abaixo, precisa das conexões semânticas já inferidas
        # para responder 15.1/15.2/15.3 (convergência/divergência/
        # similaridade), então a inferência roda antes, não depois.
        connections = []
        if len(self.graph.nodes) > 1:
            connections = infer(self.graph, iec, threshold=inference_threshold)
            for source, target, score in connections:
                self.graph.add_edge(source, target, "semantic_relation", score)

        self.coordinator.record_step(
            iec_id=iec.id, step="REASONING_ENGINE", module="inference.infer",
            inputs={"threshold": inference_threshold, "graph_size": len(self.graph.nodes)},
            outputs={"connections": connections},
            justification="Inferência semântica contra os nós já existentes no grafo.",
        )

        # 3. SCIENTIFIC_CONTEXT_RECONSTRUCTION
        # infer() sempre retorna (iec.id, outro_id, score) -- ver
        # inference/inference.py -- então o id conectado é sempre o
        # segundo elemento da tupla.
        connected_ids = [target_id for _, target_id, _ in connections]
        panorama = self.context_engine.reconstruct_context(contract, connected_iec_ids=connected_ids)
        self.coordinator.transition_state(iec.id, "EM_CONTEXTUALIZACAO", "Panorama científico reconstruído.")
        self.coordinator.record_step(
            iec_id=iec.id, step="SCIENTIFIC_CONTEXT_RECONSTRUCTION", module="ScientificContextEngine",
            inputs={"connected_iec_ids": connected_ids},
            outputs=panorama,
            justification="DOCUMENTO 23, Art. 13º-19º: reconstrói o contexto científico da IEC nova.",
        )

        # FASE 5 (PROPOSTA) -- Consensus: registra a classificação de
        # consenso deste Panorama Científico assim que ele existe.
        # Fora do ciclo oficial do Art. 5º (ver nota em workflow.py) --
        # por isso não vira um passo do coordinator, só um resultado
        # extra devolvido por run().
        consensus_result = None
        if self.consensus_engine is not None:
            consensus_result = self.consensus_engine.record_panorama(iec.id, panorama)

        # 4. VALIDATION_ENGINE
        validation_result = self.validation_engine.validate_iec(iec.id)
        semantic_validation = None
        if self.ontology_validator is not None:
            # Read-only semantic diagnostics over the graph as it exists after
            # structural validation. Never changes validation_result or graph.
            semantic_validation = self.ontology_validator.validate_graph(self.graph)
        self.coordinator.transition_state(iec.id, "EM_VALIDACAO", "Passou para validação estrutural.")
        self.coordinator.record_step(
            iec_id=iec.id, step="VALIDATION_ENGINE", module="ValidationEngine",
            inputs={"iec_id": iec.id},
            outputs=validation_result or {},
            justification="Recalcula confiança estrutural a partir da evidência disponível.",
        )

        # 5. KNOWLEDGE_EVOLUTION_ENGINE — a IEC já foi registrada mais
        # cedo (ver acima); aqui roda a avaliação real baseada em
        # evidência.
        evolution_result = self.evolution_engine.apply_evolution(
            iec.id, reason="avaliação inicial do ciclo cognitivo"
        )
        self.coordinator.transition_state(iec.id, "EM_EVOLUCAO", "Passou para avaliação evolutiva.")
        self.coordinator.record_step(
            iec_id=iec.id, step="KNOWLEDGE_EVOLUTION_ENGINE", module="KnowledgeEvolutionEngine",
            inputs={"iec_id": iec.id},
            outputs=evolution_result,
            justification="Estado epistemológico avaliado a partir da força de evidência atual.",
        )

        # 6. CURIOSITY_ENGINE
        priority = self.curiosity_engine.prioritize_research(contract)
        self.coordinator.record_step(
            iec_id=iec.id, step="CURIOSITY_ENGINE", module="CuriosityEngine",
            inputs={"iec_id": iec.id},
            outputs=priority,
            justification="Avalia se a IEC tem lacuna de evidência relevante.",
        )

        # FASE 5 (PROPOSTA) -- Discovery Lab: organiza a lacuna já
        # identificada acima + as conexões já inferidas (passo 2) em
        # um candidato a hipótese estruturado. Mesma nota de escopo:
        # fora do ciclo oficial, não vira passo do coordinator.
        hypothesis_candidate = None
        if self.discovery_lab_engine is not None:
            hypothesis_candidate = self.discovery_lab_engine.generate_hypothesis_candidate(
                iec.id, connected_iec_ids=connected_ids,
            )

        # 7. SCIENTIFIC_RESEARCH_ENGINE — condicional (ver nota em workflow.py)
        research_plan: Optional[Dict[str, Any]] = None
        if priority["priority"] <= self.SRE_TRIGGER_PRIORITY:
            task = self.curiosity_engine.request_research(contract)
            research_plan = self.research_engine.receive_research_task(task)
            self.coordinator.transition_state(
                iec.id, "EM_INVESTIGACAO_CONTINUA",
                f"Prioridade {priority['priority']} ({priority['curiosity_level']}) disparou pesquisa.",
            )
        else:
            self.coordinator.transition_state(
                iec.id, "CONHECIMENTO_CONSOLIDADO",
                f"Prioridade {priority['priority']} não exige investigação adicional agora.",
            )

        self.coordinator.record_step(
            iec_id=iec.id, step="SCIENTIFIC_RESEARCH_ENGINE", module="ScientificResearchEngine",
            inputs={"triggered": research_plan is not None},
            outputs=research_plan or {"status": "SKIPPED", "reason": "prioridade não crítica"},
            justification="Gatilho Curiosity -> Scientific Research (ENGINE-006/007, sessão de 07/08/2026).",
        )

        # 8. RESEARCH_STRATEGY_ENGINE
        opportunity = self.strategy_engine.evaluate_opportunity(iec.id, panorama)
        self.coordinator.record_step(
            iec_id=iec.id, step="RESEARCH_STRATEGY_ENGINE", module="ResearchStrategyEngine",
            inputs={"iec_id": iec.id},
            outputs=opportunity,
            justification="DOCUMENTO 25: pontua a oportunidade e sugere próximo passo (caráter consultivo, Art. 9º).",
        )

        # 9. ATUALIZACAO_DA_INTERFACE — não aplicável (sem interface neste backend)
        self.coordinator.record_step(
            iec_id=iec.id, step="ATUALIZACAO_DA_INTERFACE", module="N/A",
            inputs={}, outputs={"status": "NAO_APLICAVEL"},
            justification="Este projeto é só backend; não há interface para atualizar.",
        )

        # 10. AGUARDAR NOVAS EVIDENCIAS — encerra o ciclo ativo, não a investigação
        self.coordinator.end_cycle(iec.id)

        return {
            "iec": iec,
            "capture": capture,
            "parsi": parsi_result,
            "panorama": panorama,
            "validation": validation_result,
            "semantic_validation": semantic_validation,
            "evolution": evolution_result,
            "connections": connections,
            "priority": priority,
            "research_plan": research_plan,
            "opportunity": opportunity,
            "consensus": consensus_result,
            "hypothesis_candidate": hypothesis_candidate,
            "cycle": self.coordinator.get_cycle(iec.id),
        }
