def compute_system_health(graph, model):
    density = len(graph.edges) / max(1, len(graph.nodes))
    return {
        "graph_density": density,
        "inference_error": model.error_rate,
        "stability_index": 1 - model.error_rate,
    }
