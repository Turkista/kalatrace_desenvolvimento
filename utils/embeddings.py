"""
utils/embeddings.py

Camada de geração de vetores semânticos (KALATRACE 2.0).

Comportamento:
- Tenta usar sentence-transformers (modelo real: all-MiniLM-L6-v2), exatamente
  como especificado no documento da versão 2.0.
- Se o modelo não puder ser baixado (sem internet, ambiente restrito, etc.),
  cai automaticamente para um "hashing embedding" determinístico — um vetor
  de bag-of-words com hashing, só para manter o sistema funcional offline.
  Isso é um SUBSTITUTO DE DEMONSTRAÇÃO, não semântica real: duas frases com
  as mesmas palavras vão parecer semelhantes; frases sinônimas mas com
  palavras diferentes (o objetivo real da 2.0) NÃO serão detectadas nesse
  modo. Quando este projeto rodar num ambiente com acesso à internet, o
  modelo real é usado automaticamente e a similaridade passa a ser semântica
  de verdade, sem precisar alterar nenhum outro arquivo.
"""

import hashlib
import math
import os

_MODEL = None
_MODEL_LOAD_ATTEMPTED = False
_USING_FALLBACK = False

HASH_DIM = 256  # dimensão do vetor de fallback


def _try_load_real_model():
    global _MODEL, _MODEL_LOAD_ATTEMPTED, _USING_FALLBACK
    if _MODEL_LOAD_ATTEMPTED:
        return
    _MODEL_LOAD_ATTEMPTED = True
    try:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        _USING_FALLBACK = False
    except Exception as e:
        # Sem internet, sem pacote instalado, ou qualquer outra falha:
        # cai para o modo offline determinístico.
        _MODEL = None
        _USING_FALLBACK = True
        if os.environ.get("KALATRACE_VERBOSE"):
            print(f"[embeddings] Modelo real indisponível ({e}). Usando fallback offline.")


def _fallback_embedding(text: str, dim: int = HASH_DIM):
    """Bag-of-words determinístico via hashing. Só para uso offline/demo."""
    vec = [0.0] * dim
    words = text.lower().split()
    if not words:
        return vec
    for w in words:
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def is_using_fallback() -> bool:
    _try_load_real_model()
    return _USING_FALLBACK


def get_embedding(text: str):
    _try_load_real_model()
    if _MODEL is not None:
        return _MODEL.encode(text).tolist()
    return _fallback_embedding(text)


def cosine_similarity(vec1, vec2):
    import numpy as np
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
    if denom == 0:
        return 0.0
    return float(np.dot(v1, v2) / denom)
