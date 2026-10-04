from graph.knowledge_graph import KnowledgeGraph
from engines.reasoning.reasoning_engine import ReasoningEngine
from storage.evidence_store import EvidenceStore
from validation.validation_engine import ValidationEngine
from engines.curiosity.curiosity_engine import CuriosityEngine
from engines.scientific_research.scientific_research_engine import ScientificResearchEngine
from contracts.iec_contract import IECContract
from knowledge.iec import IEC

# -----------------------------
# SISTEMA
# -----------------------------
graph = KnowledgeGraph()
reasoner = ReasoningEngine(graph)
evidence_store = EvidenceStore()
validator = ValidationEngine(graph, evidence_store)
# CuriosityEngine real (engines/curiosity/curiosity_engine.py) recebe só
# evidence_store -- a versão anterior deste demo chamava
# CuriosityEngine(graph, evidence_store, validator) e um método
# suggest_next_exploration() que nunca existiram na classe atual (ver
# engines/curiosity/curiosity_engine.py). Adaptado abaixo para a API real:
# analyze_gap()/prioritize_research() esperam um contracts.IECContract, não
# o objeto IEC "de brinquedo" deste script -- por isso construímos um
# IECContract por nó na hora de consultar a curiosidade.
curiosity = CuriosityEngine(evidence_store)

# ScientificResearchEngine (roadmap de estabilização, ENGINE-006/007,
# sessão de 07/08/2026): estava órfão, sem nenhum consumidor de produção,
# apesar de já ter sido escrito para receber tarefas do CuriosityEngine --
# CuriosityEngine.create_research_task() diz literalmente "for the future
# Scientific Research Engine", e ScientificResearchEngine.receive_research_task()
# diz literalmente "Recebe uma tarefa criada pelo CuriosityEngine". O
# gatilho é o fluxo que create_research_task/request_research já
# documentava: IEC com lacuna -> Curiosity Analysis -> Research Task ->
# Queue -> SRE. Nenhuma lógica nova foi inventada, só a ligação entre os
# dois contratos que já existiam.
sre = ScientificResearchEngine(evidence_store)

# -----------------------------
# IECs
# -----------------------------
# knowledge.iec.IEC (importado acima) substitui a classe local "de
# brinquedo" que existia aqui antes: ela só tinha id/content, e
# ValidationEngine.validate_iec() precisa de confidence/status/
# update_confidence, que só a classe real tem.

iec1 = IEC("IEC-001", "Bakuchiol estimula síntese de colágeno")
iec2 = IEC("IEC-002", "Colágeno melhora regeneração da pele")
iec3 = IEC("IEC-003", "Inflamação reduz síntese de colágeno")  # mais fraco

graph.add_node(iec1)
graph.add_node(iec2)
graph.add_node(iec3)

# -----------------------------
# RELAÇÕES
# -----------------------------
graph.add_edge("IEC-001", "IEC-002", "causa_indireta", 0.8)
graph.add_edge("IEC-003", "IEC-001", "inibe", 0.6)

# -----------------------------
# EVIDÊNCIA
# -----------------------------
# EvidenceStore.add_evidence() exige um EvidenceContract, não argumentos
# posicionais soltos -- create_evidence() é o atalho real que já monta o
# contrato e chama add_evidence() por baixo (ver storage/evidence_store.py).
# link_to_iec() é o que efetivamente associa a evidência ao IEC: sem ele,
# compute_evidence_strength()/analyze_gap() não encontram nada para o nó.
evidence_store.create_evidence(
    "EVD-001",
    "Journal of Dermatology 2023",
    "clinical_study",
    "Bakuchiol e síntese de colágeno",
    "Journal of Dermatology 2023",
    0.85
)
evidence_store.link_to_iec("EVD-001", "IEC-001")

evidence_store.create_evidence(
    "EVD-002",
    "Skin Biology Review 2022",
    "review",
    "Colágeno e regeneração da pele",
    "Skin Biology Review 2022",
    0.75
)
evidence_store.link_to_iec("EVD-002", "IEC-002")

# IEC-003 propositalmente sem evidência forte

# -----------------------------
# EXECUÇÃO
# -----------------------------
print("KALATRACE iniciado 🚀")

print("\n--- GRAFO ---")
print("Nós:", graph.nodes)
print("Edges:", graph.edges)

print("\n--- RACIOCÍNIO ---")
print(reasoner.explain_connection("IEC-001", "IEC-002"))

print("\n--- VALIDAÇÃO ---")
print(validator.validate_all())

print("\n--- CURIOSIDADE (PRIORIDADES DE EXPLORAÇÃO) ---")
priorities = []
for node_id, node in graph.nodes.items():
    contract = IECContract(
        iec_id=node_id,
        title=node.content[:40],
        statement=node.content,
        knowledge_type="Conhecimento",
    )
    priorities.append((contract, curiosity.prioritize_research(contract)))

for _, item in sorted(priorities, key=lambda p: p[1]["priority"]):
    print(item)

# --- GATILHO DO SCIENTIFIC RESEARCH ENGINE ---
# Só IECs com lacuna significativa (CRITICAL/HIGH, priority 1 ou 2 --
# ver CuriosityEngine.prioritize_research) disparam uma tarefa de
# pesquisa automática. Threshold escolhido a partir da própria semântica
# de prioridade do CuriosityEngine, não um valor arbitrário novo.
print("\n--- SCIENTIFIC RESEARCH (TAREFAS DISPARADAS PELA CURIOSIDADE) ---")
research_plans = []
for contract, item in priorities:
    if item["priority"] <= 2:
        task = curiosity.request_research(contract)
        plan = sre.receive_research_task(task)
        research_plans.append(plan)

if research_plans:
    for plan in research_plans:
        print(plan)
else:
    print("  (nenhuma IEC com lacuna CRITICAL/HIGH nesta rodada)")
