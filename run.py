"""
run.py — KALATRACE unificado (1.0 -> 4.0 + curadoria + orquestração)

Ciclo por IEC, coordenado pelo Cognitive Orchestrator (DOCUMENTO 26)
[roadmap de estabilização, sessão de 08/08/2026]:
  0. Aquisição manual (ManualAcquisition)                    [DOC 23]
  1. Criação da IEC + integração ao grafo
  2. Raciocínio: inferência semântica contra o grafo existente
  3. Reconstrução de contexto científico (SCR)                [DOC 23, Parte III]
  4. Validação estrutural (ValidationEngine)
  5. Evolução epistemológica (Knowledge Evolution Engine)     [ENGINE-006]
  6. Curiosidade -> gatilho do Scientific Research Engine     [ENGINE-006/007]
  7. Estratégia de pesquisa (Research Strategy Engine)        [DOC 25]

Dentro do próprio ciclo, mas fora do Art. 5º oficial (FASE 5
PROPOSTA -- Camada Cognitiva Avançada, sessão de 09/08/2026):
  - Consensus: rastreia a classificação de consenso de cada
    Panorama Científico e detecta mudança entre reconstruções.
  - Discovery Lab: organiza a lacuna do CuriosityEngine + as
    conexões já inferidas em candidatos a hipótese estruturados.
(Ver docstring de CognitiveOrchestrator/CyclePipeline para por que
os dois não viram passo do coordinator.)

Depois que todas as IECs passaram pelo ciclo (etapas fora do
Cognitive Orchestrator, porque operam sobre o grafo consolidado,
não sobre uma IEC isolada):
  6. Governança: avaliar e filtrar conexões       [3.0]
  7. Evolução do grafo: reforçar/podar arestas    [3.0]
  8. Metacognição: o sistema observa a si mesmo   [4.0]
  9. Curadoria: maturidade, confiabilidade,
     duplicidades, lacunas, conflitos             [Blueprint Doc. 5]
  10. Memória: persistir tudo em JSON

Também fora do Art. 5º, chamado uma vez ao final (não por IEC):
  Dynamic: adapta o plano do Research Strategy Engine com os
  sinais de controvérsia já observados pelo Consensus.

Nota sobre "Evolução" (passo 3 vs. passo 7): a do passo 3 é
epistemológica (estado de sustentação de cada IEC por evidências,
via KnowledgeEvolutionEngine); a do passo 7 é estrutural (reforça/
poda arestas do grafo, via evolution/optimizer.py). Nomes que já
existiam separados no projeto; mantidos assim para não confundir os
dois motores.

Nota sobre a mudança de estrutura desta sessão: antes, cada passo
do ciclo (aquisição, evolução, inferência, curiosidade) era ligado
manualmente aqui, chamada por chamada -- o problema que o DOCUMENTO
26, Art. 7º, descreve ("os módulos não deverão depender diretamente
uns dos outros"). Agora, um único CognitiveOrchestrator coordena os
passos 0-5 para cada IEC; run.py só chama run_cycle() e usa o
resultado. Efeito colateral esperado (não é regressão): como o
Orchestrator roda inferência a cada IEC nova contra o grafo já
existente (não só para a última, "hipótese"), agora as IECs 2, 3 e
4 também geram conexões inferidas contra as anteriores -- mais
fiel ao ciclo oficial (toda IEC nova é investigada), não só a
última.
"""

from utils.embeddings import is_using_fallback
from engines.cognitive_orchestrator.cognitive_orchestrator_engine import CognitiveOrchestrator
from governance.evaluator import Evaluator
from evolution.optimizer import Optimizer
from metacognition.self_model import SelfModel
from metacognition.observer import Observer
from metacognition.metrics import compute_system_health
from curation.curation import (
    maturity_label, reliability_score, classify_knowledge_state,
    detect_duplicates, detect_gaps, detect_conflicts,
)
from memory.memory_manager import save_graph


def main():
    if is_using_fallback():
        print("⚠️  Rodando com embedding OFFLINE (fallback por hashing).")
        print("   Sem internet para baixar o modelo real (sentence-transformers).")
        print("   Instale as dependências e rode com internet para semântica real.\n")

    orchestrator = CognitiveOrchestrator()
    threshold = 0.3 if is_using_fallback() else 0.55

    # Submissões que um pesquisador enviaria pela interface do
    # MEDIKALAT: (statement, node_type, quem submeteu). As 3 primeiras
    # entram sem evidência vinculada -- o Cognitive Orchestrator ainda
    # assim roda o ciclo completo para cada uma (validação, evolução,
    # inferência, curiosidade), com o resultado honesto de UNKNOWN
    # onde não há sustentação (DOCUMENTO 30, Princípio 6: confiança não
    # é gratuita).
    raw_submissions = [
        ("bakuchiol reduz marcadores de inflamação cutânea", "Evidência", "Dra. Ana (MEDIKALAT)"),
        ("resveratrol ativa a expressão de SIRT1 em fibroblastos", "Evidência", "Dr. Bruno (MEDIKALAT)"),
        ("bakuchiol estimula a produção de colágeno tipo I", "Evidência", "Dra. Ana (MEDIKALAT)"),
        ("protocolo de ensaio de toxicidade aguda em modelo animal", "Experimento", "Dr. Carlos (MEDIKALAT)"),
    ]

    cycle_results = [
        orchestrator.run_cycle(statement, author, submission_type=node_type, inference_threshold=threshold)
        for statement, node_type, author in raw_submissions
    ]
    iec1 = cycle_results[0]["iec"]

    # Evidência de exemplo vinculada só à primeira IEC (mesmo espírito
    # do bloco de Curadoria mais abaixo: "exemplo de uso manual; numa
    # versão real viria de dados reais do estudo") -- demonstra o
    # ciclo completo (evidência chega depois -> evolução é reavaliada)
    # sem fingir sustentação que as outras IECs não têm.
    orchestrator.evidence_store.create_evidence(
        "ev-1", source="PubMed (exemplo)", evidence_type="in_vitro",
        title="Estudo exemplo sobre bakuchiol e inflamação cutânea",
        description="Evidência de exemplo — numa versão real viria da camada de aquisição científica.",
        confidence=0.75,
    )
    orchestrator.evidence_store.link_to_iec("ev-1", iec1.id)
    orchestrator.evolution_engine.apply_evolution(iec1.id, reason="evidência de exemplo vinculada")
    # Reavalia a oportunidade de iec1 no Research Strategy Engine (Art.
    # 6º, DOCUMENTO 25: "sempre que o estado do conhecimento evoluir,
    # as prioridades poderão ser reorganizadas") -- sem isso, o plano
    # estratégico final ficaria com a avaliação de antes da evidência
    # chegar, incoerente com o resto do relatório.
    iec1_panorama = orchestrator.context_engine.reconstruct_context(
        iec1.to_contract(), connected_iec_ids=[t for _, t, _ in cycle_results[0]["connections"]]
    )
    orchestrator.strategy_engine.evaluate_opportunity(iec1.id, iec1_panorama)
    # FASE 5 (PROPOSTA) -- Consensus: mesma razão da reavaliação acima,
    # esta reconstrução de contexto foi manual (fora de run_cycle), então
    # não passou pelo registro automático em CyclePipeline.run().
    orchestrator.consensus_engine.record_panorama(iec1.id, iec1_panorama)

    # Novo conhecimento chega ao sistema (uma hipótese, depois das 4
    # evidências/experimento de base já no grafo) -> ciclo completo de
    # novo, incluindo inferência contra tudo que já existe.
    hypothesis_result = orchestrator.run_cycle(
        "bakuchiol tem atividade antioxidante e reduz inflamação na pele",
        "Sistema (hipótese derivada)",
        submission_type="Hipótese",
        inference_threshold=threshold,
    )

    graph = orchestrator.graph
    all_connections = [c for r in cycle_results + [hypothesis_result] for c in r["connections"]]

    # 6. Governança — avalia e filtra conexões fracas
    evaluator = Evaluator()
    graph = evaluator.filter_edges(graph, min_score=0.15 if is_using_fallback() else 0.4)

    # 7. Evolução do grafo — reforça conexões boas, poda o resto
    optimizer = Optimizer()
    graph = optimizer.reinforce_edges(graph)
    graph = optimizer.prune_graph(graph, threshold=0.1)

    # 8. Metacognição — o sistema observa o próprio ciclo
    self_model = SelfModel()
    observer = Observer(self_model)
    metacog_report = observer.monitor_cycle(graph, all_connections)
    health = compute_system_health(graph, self_model)

    # 9. Curadoria — classificação epistemológica (exemplo de uso manual;
    #    numa versão real esses fatores viriam de dados reais do estudo)
    example_factors = {
        "methodological_quality": 0.8,
        "sample_size": 0.6,
        "bias_risk_inverted": 0.7,
        "reproducibility": 0.75,
        "statistical_consistency": 0.8,
        "recency": 0.9,
    }
    rel_score = reliability_score(example_factors)
    maturity_score = 68  # exemplo — na prática, calculado a partir do nº/qualidade de estudos
    state = classify_knowledge_state(maturity_score, rel_score)

    duplicates = detect_duplicates(graph, threshold=0.85 if is_using_fallback() else 0.92)
    gaps = detect_gaps(graph)
    conflicts = detect_conflicts(graph, similarity_threshold=0.3 if is_using_fallback() else 0.6)

    # 10. Memória
    save_graph(graph, filename="graph.json")

    # ---- Relatório do ciclo ----
    print("=== GRAFO ===")
    print(graph)
    print("\n=== AQUISIÇÃO MANUAL (ManualAcquisition) ===")
    print(" ", orchestrator.acquisition.stats())
    print("\n=== CICLO COGNITIVO (Cognitive Orchestrator) ===")
    for state_name, state_count in orchestrator.state_distribution().items():
        print(f"  {state_name}: {state_count} IEC(s)")
    print("\n=== EVOLUÇÃO EPISTEMOLÓGICA (Knowledge Evolution Engine) ===")
    for result in cycle_results + [hypothesis_result]:
        summary = orchestrator.evolution_engine.generate_summary(result["iec"].id)
        print(f"  {result['iec'].id}: estado={summary['current_state']}  direção={summary['direction']}")
    print("\n=== CONEXÕES INFERIDAS ===")
    for s, t, score in all_connections:
        print(f"  {s} -> {t}  (score={score:.3f})")
    print("\n=== CONTEXTO CIENTÍFICO (Scientific Context Reconstruction) ===")
    for result in cycle_results + [hypothesis_result]:
        panorama = result["panorama"]
        print(
            f"  {panorama['iec_id']}: consenso={panorama['scientific_consensus']}"
            f"  convergentes={len(panorama['convergent_evidence'])}"
            f"  divergentes={len(panorama['divergent_evidence'])}"
        )
    print("\n=== SCIENTIFIC RESEARCH (TAREFAS DISPARADAS PELA CURIOSIDADE) ===")
    triggered = [r["research_plan"] for r in cycle_results + [hypothesis_result] if r["research_plan"]]
    if triggered:
        for plan in triggered:
            print(" ", plan)
    else:
        print("  (nenhuma IEC com lacuna CRITICAL/HIGH nesta rodada)")
    print("\n=== ESTRATÉGIA DE PESQUISA (Research Strategy Engine) ===")
    plan = orchestrator.build_strategic_plan()
    for item in plan["ranked_opportunities"]:
        print(
            f"  {item['iec_id']}: score={item['priority']['composite_score']}"
            f"  recomendação={item['strategy']['recommendation']}"
            f"  ({item['strategy']['justification']})"
        )
    print("\n=== CONSENSUS (FASE 5 PROPOSTA) ===")
    landscape = orchestrator.consensus_engine.consensus_landscape()
    print(f"  Panorama agregado: {landscape['distribution']} ({landscape['tracked_iecs']} IEC(s) rastreadas)")
    controversial = orchestrator.consensus_engine.controversial_iecs()
    print(f"  IECs controversas: {controversial if controversial else '(nenhuma nesta rodada)'}")

    print("\n=== DISCOVERY LAB (FASE 5 PROPOSTA) ===")
    for candidate in orchestrator.discovery_lab_engine.qualifying_candidates():
        print(
            f"  {candidate['iec_id']}: {candidate['exploration_type']}"
            f"  curiosidade={candidate['curiosity_level']}"
            f"  conectadas={candidate['connected_iec_ids']}"
        )
    dl_stats = orchestrator.discovery_lab_engine.stats()
    print(f"  Total de candidatos: {dl_stats['total_candidates']} (qualificam: {dl_stats['qualifying_candidates']})")

    print("\n=== DYNAMIC (FASE 5 PROPOSTA) ===")
    adapted = orchestrator.adapt_strategy()
    for item in adapted["adapted_plan"]["ranked_opportunities"]:
        print(
            f"  {item['iec_id']}: score_ajustado={item['adjusted_score']}"
            f"  ajuste={item['strategy_adjustment']}"
        )
    if adapted["priority_shift"]:
        print(f"  Mudança de prioridade no topo do plano: {adapted['priority_shift']}")
    else:
        print("  (sem plano adaptado anterior para comparar mudança de prioridade)")

    print("\n=== METACOGNIÇÃO ===")
    print(" ", metacog_report)
    print("\n=== SAÚDE DO SISTEMA ===")
    print(" ", health)
    print("\n=== CURADORIA (exemplo) ===")
    print(f"  Maturidade: {maturity_score}% -> {maturity_label(maturity_score)}")
    print(f"  Confiabilidade: {rel_score}%")
    print(f"  Estado do conhecimento: {state}")
    print(f"  Duplicidades detectadas: {duplicates}")
    print(f"  Lacunas detectadas: {gaps}")
    print(f"  Conflitos detectados: {conflicts}")


if __name__ == "__main__":
    main()
