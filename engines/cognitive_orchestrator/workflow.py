from typing import Tuple


# ==========================================================
# CICLO COGNITIVO OFICIAL (DOCUMENTO 26 — Cognitive Orchestrator,
# Art. 5º "O Ciclo Cognitivo")
# ==========================================================
#
# Cada item: (nome do passo, módulo real que o executa nesta
# implementação -- ou None se o módulo ainda não existe no
# projeto).
#
# "Aguardar Novas Evidências" (último passo do Art. 5º) não é um
# passo executável -- é o próprio encerramento do ciclo, tratado
# pelo CognitiveOrchestrator, não listado aqui.

CYCLE_STEPS: Tuple[Tuple[str, str], ...] = (
    ("AQUISICAO_DO_CONHECIMENTO", "IMPLEMENTADO"),
    ("SCIENTIFIC_RESEARCH_ENGINE", "IMPLEMENTADO_CONDICIONAL"),
    ("SCIENTIFIC_CONTEXT_RECONSTRUCTION", "IMPLEMENTADO"),
    ("VALIDATION_ENGINE", "IMPLEMENTADO"),
    ("KNOWLEDGE_EVOLUTION_ENGINE", "IMPLEMENTADO"),
    ("KNOWLEDGE_GRAPH", "IMPLEMENTADO"),
    ("REASONING_ENGINE", "IMPLEMENTADO_CONDICIONAL"),
    ("CURIOSITY_ENGINE", "IMPLEMENTADO"),
    ("RESEARCH_STRATEGY_ENGINE", "IMPLEMENTADO"),
    ("ATUALIZACAO_DA_INTERFACE", "NAO_APLICAVEL"),
)

# Nota sobre a ordem real de execução nesta implementação vs. o
# Art. 5º: o DOCUMENTO 26 coloca o Scientific Research Engine logo
# após a Aquisição -- investigar a literatura antes de qualquer
# outra coisa. Nesta implementação, porém, o único gatilho real que
# existe para o SRE é o CuriosityEngine (ver ENGINE-006/007,
# roadmap de estabilização, sessão de 07/08/2026: "create_research_task
# for the future Scientific Research Engine" / "Recebe uma tarefa
# criada pelo CuriosityEngine"), e o CuriosityEngine só consegue
# avaliar prioridade depois que existe alguma evidência vinculada
# (ainda que nenhuma, o que já é um sinal). Por isso, nesta
# implementação, SCIENTIFIC_RESEARCH_ENGINE é avaliado DEPOIS de
# CURIOSITY_ENGINE, não logo após a aquisição -- desvio documentado,
# não silencioso. IMPLEMENTADO_CONDICIONAL marca passos que só
# executam quando a condição real do projeto permite (SRE: só se
# CuriosityEngine sinalizar prioridade CRITICAL/HIGH; Reasoning: só
# se já existir mais de 1 nó no grafo para inferir conexão).


# ==========================================================
# ESTADOS COGNITIVOS (DOCUMENTO 26, Art. 6º)
# ==========================================================

COGNITIVE_STATES: Tuple[str, ...] = (
    "NOVO_CONHECIMENTO",
    "EM_CONTEXTUALIZACAO",
    "EM_VALIDACAO",
    "EM_EVOLUCAO",
    "EM_INVESTIGACAO_CONTINUA",
    "NECESSITA_EVIDENCIAS",
    "PRIORIDADE_ESTRATEGICA",
    "CONHECIMENTO_CONSOLIDADO",
)

# Nota: EM_CONTEXTUALIZACAO já é atingido nesta implementação
# (SCIENTIFIC_CONTEXT_RECONSTRUCTION, sessão de 08/08/2026).
# PRIORIDADE_ESTRATEGICA ainda não é atingido dentro do ciclo por
# IEC -- o Research Strategy Engine (implementado na mesma sessão)
# avalia oportunidades e monta planos, mas isso acontece por fora
# do ciclo individual de cada IEC (engines/cognitive_orchestrator/
# pipeline.py chama evaluate_opportunity a cada ciclo, mas quem
# decide gerar/consultar o plano ranqueado, com várias oportunidades
# comparadas entre si, é quem usa o CognitiveOrchestrator -- não faz
# sentido reranquear o plano inteiro a cada IEC nova sozinha).
