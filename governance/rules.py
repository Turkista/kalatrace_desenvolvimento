"""
governance/rules.py

Regras epistemológicas do KALATRACE.

Este módulo concentra critérios
utilizados pela camada Governance
para avaliar qualidade estrutural
do conhecimento.

As regras não representam verdade
científica.

Elas representam critérios mínimos
de sustentação e consistência.
"""



# ==========================================================
# LIMIARES EPISTEMOLÓGICOS
# ==========================================================


MIN_EDGE_WEIGHT: float = 0.4
"""
Peso mínimo permitido para uma conexão
do grafo.

Valores abaixo indicam relação estrutural
fraca.
"""


MIN_SIMILARITY: float = 0.5
"""
Similaridade mínima entre representações
semânticas de dois nós.
"""



# ==========================================================
# VALIDAÇÕES DE GOVERNANÇA
# ==========================================================


def is_valid_connection(
    score: float,
) -> bool:
    """
    Determines whether a connection
    satisfies minimum governance quality.

    Parameters:

    score:
        Final epistemological score
        calculated by Evaluator.

    Returns:

    True:
        Connection accepted.

    False:
        Connection rejected.
    """


    if not isinstance(
        score,
        (float, int),
    ):
        raise TypeError(
            "score must be numeric."
        )


    return score >= MIN_EDGE_WEIGHT



def is_valid_similarity(
    similarity: float,
) -> bool:
    """
    Validates semantic similarity
    between knowledge nodes.
    """


    if not isinstance(
        similarity,
        (float, int),
    ):
        raise TypeError(
            "similarity must be numeric."
        )


    return similarity >= MIN_SIMILARITY