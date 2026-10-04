from utils.embeddings import cosine_similarity


def simple_similarity(text1, text2):
    """Similaridade por palavras em comum (Jaccard) — método da 1.0.
    Mantido como utilitário auxiliar/fallback de baixo custo."""
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    if not set1 or not set2:
        return 0
    return len(set1.intersection(set2)) / len(set1.union(set2))


def infer(graph, new_iec, threshold: float = 0.55):
    """Inferência semântica real (2.0): compara embeddings via cosseno.
    Retorna lista de (source_id, target_id, score) para toda conexão
    que ultrapassa o limiar."""
    connections = []
    for node_id, node in graph.nodes.items():
        if node_id == new_iec.id:
            continue
        score = cosine_similarity(new_iec.embedding, node.embedding)
        if score >= threshold:
            connections.append((new_iec.id, node_id, score))
    return connections
