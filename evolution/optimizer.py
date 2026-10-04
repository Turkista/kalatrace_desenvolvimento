class Optimizer:
    """O 'otimizador' (3.0): reforça conexões boas, enfraquece as ruins,
    e remove o que ficou irrelevante — evolução primitiva do grafo."""

    def reinforce_edges(self, graph):
        for edge in graph.edges:
            if edge.get("quality_score", 0) > 0.7:
                edge["weight"] *= 1.1
            else:
                edge["weight"] *= 0.9
        return graph

    def prune_graph(self, graph, threshold: float = 0.3):
        graph.edges = [e for e in graph.edges if e["weight"] >= threshold]
        return graph
