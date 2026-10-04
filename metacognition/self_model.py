class SelfModel:
    """Modelo interno de comportamento do sistema (4.0).

    NOTA HONESTA: `error_rate` aqui é um placeholder deliberado (o próprio
    documento da 4.0 o chama de "simulação de métrica interna"). Ele cresce
    artificialmente com o volume de inferências, só para ter um número a
    reportar. Isso ainda NÃO é medição real de erro — para virar real,
    precisa de um "gabarito" (ex: curador humano corrigindo/confirmando
    inferências) que alimente essa métrica com dados verdadeiros. O gancho
    para isso é `log_correction()`, adicionado aqui para o próximo passo.
    """

    def __init__(self):
        self.inference_history = []
        self.corrections = []  # feedback humano real, quando existir
        self.error_rate = 0.0
        self.confidence_bias = 1.0

    def log_inference(self, input_data, output_data):
        self.inference_history.append({
            "input": input_data,
            "output": output_data,
        })

    def log_correction(self, inference_index: int, was_correct: bool):
        """Gancho para aprendizado real: quando um curador confirma ou
        rejeita uma inferência, isso entra aqui em vez do placeholder."""
        self.corrections.append({"index": inference_index, "correct": was_correct})

    def analyze_behavior(self):
        total = len(self.inference_history)
        if total == 0:
            return {"status": "no data"}

        if self.corrections:
            wrong = sum(1 for c in self.corrections if not c["correct"])
            self.error_rate = wrong / len(self.corrections)
        else:
            # placeholder documentado — substitua por dados reais quando houver
            self.error_rate = min(1.0, total * 0.01)

        return {
            "inferences": total,
            "error_rate": self.error_rate,
            "error_rate_is_real": bool(self.corrections),
        }
