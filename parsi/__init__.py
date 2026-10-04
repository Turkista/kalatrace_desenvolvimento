"""PARSI — primeiro estágio cognitivo do KALATRACE.

O módulo interpreta entradas brutas e produz representação semântica
estruturada. Não valida conhecimento científico nem altera o grafo.
"""

from parsi.models import PARSIResult, SemanticContext, SemanticEntity, SemanticRelation
from parsi.parsi_engine import PARSI, PARSIEngine

__all__ = [
    "PARSI",
    "PARSIEngine",
    "PARSIResult",
    "SemanticContext",
    "SemanticEntity",
    "SemanticRelation",
]
