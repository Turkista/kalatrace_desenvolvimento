from knowledge.iec import IEC
from utils.embeddings import get_embedding


class CoreEngine:
    """Fábrica de IECs. Ponto único de criação de conhecimento no sistema."""

    def create_iec(self, id, content, node_type="Conhecimento", metadata=None):
        # IEC.__init__ recebe `domain`, não `node_type` (node_type é uma
        # property de compatibilidade em knowledge/iec.py); passamos o
        # valor recebido aqui para o parâmetro real.
        iec = IEC(id=id, content=content, domain=node_type, metadata=metadata)
        # inference/inference.py compara new_iec.embedding com node.embedding
        # via cosseno, mas nada nunca calculava e anexava esse vetor -- sem
        # isso, toda chamada de infer() quebrava com AttributeError. Calculado
        # aqui, no único ponto de criação de IECs, para já nascer pronto.
        iec.embedding = get_embedding(content)
        return iec
