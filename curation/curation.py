"""
curation/curation.py

Implementa as partes do "Blueprint Mestre" (Documento 5 — Motor de
Curadoria e Governança do Conhecimento) que têm regra concreta o
suficiente para virar código determinístico:

  - Índice de Maturidade Científica (faixas 0-20/21-40/.../81-100)
  - Índice de Confiabilidade (média ponderada de fatores)
  - Estados de classificação do conhecimento
  - Detector de Duplicidades (similaridade muito alta entre IECs)
  - Detector de Lacunas (nós isolados no grafo)
  - Detector de Conflitos (heurística — ver nota abaixo)

O que este módulo NÃO tenta fazer: o Vetor de Ponderação Epistemológica
completo (Documento 32) e qualquer coisa da faixa "metacognição /
autoevolução arquitetural" (Documentos 34-43) — essas partes do Blueprint
não têm fórmula definida (o próprio documento trata a função de
ponderação como espaço reservado). Onde o sistema precisa desse tipo de
julgamento qualitativo, o caminho certo é uma chamada real a um modelo de
linguagem (Claude) com um prompt derivado dessas regras — não uma equação
fixa fingindo ser inteligência.
"""

from utils.embeddings import cosine_similarity

# --- Índice de Maturidade Científica -----------------------------------

MATURITY_BANDS = [
    (0, 20, "Hipótese Inicial"),
    (21, 40, "Pouca Evidência"),
    (41, 60, "Evidência Moderada"),
    (61, 80, "Forte Evidência"),
    (81, 100, "Conhecimento Consolidado"),
]


def maturity_label(maturity_score: float) -> str:
    """maturity_score: 0-100. Retorna o rótulo da faixa correspondente."""
    score = max(0, min(100, maturity_score))
    for low, high, label in MATURITY_BANDS:
        if low <= score <= high:
            return label
    return "Indefinido"


# --- Índice de Confiabilidade -------------------------------------------

# Pesos default — ajustáveis por domínio (o Blueprint prevê isso:
# Medicina prioriza evidência clínica, Engenharia prioriza validação
# experimental, etc.)
DEFAULT_RELIABILITY_WEIGHTS = {
    "methodological_quality": 0.25,   # qualidade metodológica dos estudos
    "sample_size": 0.15,              # tamanho das amostras (normalizado 0-1)
    "bias_risk_inverted": 0.20,       # 1 - risco de viés
    "reproducibility": 0.20,          # reprodutibilidade
    "statistical_consistency": 0.10,  # consistência estatística
    "recency": 0.10,                  # atualidade das evidências (0-1)
}


def reliability_score(factors: dict, weights: dict = None) -> float:
    """
    factors: dict com chaves de DEFAULT_RELIABILITY_WEIGHTS, valores 0-1.
    Chaves ausentes contam como 0 (penaliza por falta de dado, não ignora).
    Retorna score 0-100.
    """
    weights = weights or DEFAULT_RELIABILITY_WEIGHTS
    total_weight = sum(weights.values())
    score = 0.0
    for key, weight in weights.items():
        value = factors.get(key, 0.0)
        value = max(0.0, min(1.0, value))
        score += value * weight
    return round((score / total_weight) * 100, 1)


# --- Estados de classificação do conhecimento ---------------------------

KNOWLEDGE_STATES = [
    "Hipótese",
    "Evidência Emergente",
    "Conhecimento Moderado",
    "Conhecimento Consolidado",
    "Conhecimento Contestado",
    "Conhecimento Obsoleto",
]


def classify_knowledge_state(maturity_score: float, reliability_score_value: float,
                              has_active_conflict: bool = False,
                              superseded_by: str = None) -> str:
    """Máquina de estados simples, seguindo a descrição do Documento 5."""
    if superseded_by:
        return "Conhecimento Obsoleto"
    if has_active_conflict:
        return "Conhecimento Contestado"
    if maturity_score <= 20:
        return "Hipótese"
    if maturity_score <= 40:
        return "Evidência Emergente"
    if maturity_score <= 60 or reliability_score_value < 60:
        return "Conhecimento Moderado"
    return "Conhecimento Consolidado"


# --- Detector de Duplicidades --------------------------------------------

def detect_duplicates(graph, threshold: float = 0.92):
    """Pares de IECs semanticamente quase idênticos — candidatos a fusão
    ou marcação de sinônimo. Decisão final é humana (conforme o Blueprint)."""
    pairs = []
    ids = list(graph.nodes.keys())
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = graph.nodes[ids[i]], graph.nodes[ids[j]]
            sim = cosine_similarity(a.embedding, b.embedding)
            if sim >= threshold:
                pairs.append({"a": a.id, "b": b.id, "similarity": round(sim, 3)})
    return pairs


# --- Detector de Lacunas --------------------------------------------------

def detect_gaps(graph):
    """Nós sem nenhuma conexão são o sinal mais simples e concreto de
    'lacuna' que dá para detectar sem julgamento qualitativo."""
    isolated = graph.isolated_nodes()
    # isolated_nodes() retorna os objetos IEC, não os ids (ver
    # graph/knowledge_graph.py) -- iterar direto sobre os objetos.
    return [
        {
            "node_id": node.id,
            "node_type": node.node_type,
            "content": node.content,
            "message": "Poucas evidências conectando este nó ao restante do grafo.",
        }
        for node in isolated
    ]


# --- Detector de Conflitos -------------------------------------------------

_NEGATION_MARKERS = {"não", "nao", "nunca", "nenhum", "nenhuma", "sem"}


def detect_conflicts(graph, similarity_threshold: float = 0.6):
    """
    HEURÍSTICA, não julgamento científico real: procura pares de IECs
    semanticamente próximos (falam do mesmo assunto) onde um contém marcador
    de negação e o outro não — sinal de possível afirmação contraditória
    sobre o mesmo tema. Isso replica a MECÂNICA descrita no Blueprint
    (Artigo A diz X, Artigo B diz não-X), mas de forma simples; não
    substitui avaliação humana ou de um LLM lendo o conteúdo de verdade.
    """
    conflicts = []
    ids = list(graph.nodes.keys())
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = graph.nodes[ids[i]], graph.nodes[ids[j]]
            sim = cosine_similarity(a.embedding, b.embedding)
            if sim < similarity_threshold:
                continue
            a_words = set(a.content.lower().split())
            b_words = set(b.content.lower().split())
            a_neg = bool(a_words & _NEGATION_MARKERS)
            b_neg = bool(b_words & _NEGATION_MARKERS)
            if a_neg != b_neg:
                conflicts.append({
                    "a": a.id, "b": b.id,
                    "similarity": round(sim, 3),
                    "message": "Possível contradição — revisão humana recomendada.",
                })
    return conflicts
