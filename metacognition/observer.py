class Observer:
    """Observa cada ciclo do sistema e registra no SelfModel."""

    def __init__(self, self_model):
        self.model = self_model

    def monitor_cycle(self, graph, inference_results):
        self.model.log_inference(
            input_data=list(graph.nodes.keys()),
            output_data=inference_results,
        )
        return self.model.analyze_behavior()
