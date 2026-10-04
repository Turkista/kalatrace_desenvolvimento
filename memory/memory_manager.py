import json
import os


def save_graph(graph, filename: str = "graph.json"):
    data = {
        "nodes": {
            k: {
                "content": v.content,
                "node_type": v.node_type,
                "embedding": v.embedding,
                "confidence": v.confidence,
                "metadata": v.metadata,
            } for k, v in graph.nodes.items()
        },
        "edges": graph.edges,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename


def load_graph(filename: str = "graph.json"):
    if not os.path.exists(filename):
        return {"nodes": {}, "edges": []}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
