"""
KALATRACE Acquisition -- DOI Resolver

Resolve DOIs para identificar/desduplicar publicações antes de
criar IECs (DOCUMENTO 23, Seção 11, um dos módulos ainda não
implementados listados em acquisition/__init__.py).

Os 3 clientes de fonte (PubMedConnector, CrossrefClient,
SemanticScholarClient) já devolvem `doi` normalizado em cada
registro (SourceConnector._build_record já faz strip + lower),
mas o mesmo trabalho pode aparecer em mais de uma fonte com o
mesmo DOI -- é isso que este módulo resolve: agrupa registros
pelo DOI e funde os duplicados em um único registro canônico,
sem perder a rastreabilidade de qual fonte contribuiu com o quê
(DOCUMENTO 23, Seção 4).

NÃO faz parte deste módulo:

- localizar ou obter literatura (isso é SourceConnector /
  PubMedConnector / CrossrefClient / SemanticScholarClient);
- decidir se um resultado vira IEC (isso é responsabilidade de
  camadas posteriores do fluxo -- Seção 10: Contextualização,
  Comparação, Validação);
- desduplicar por título/similaridade quando não há DOI -- só
  cobre o caso identificado explicitamente por DOI. Registros
  sem DOI passam adiante sem alteração (ver `without_doi` em
  `resolve`), e ficam fora do escopo desta resolução.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from shared.enums import SourceType

__all__ = ["DOIResolver"]


class DOIResolver:
    """
    Resolve e desduplica registros de literatura pelo DOI.

    Uso:
        resolver = DOIResolver()
        resultado = resolver.resolve(registros_de_varias_fontes)
        registros_deduplicados = resultado["records"]
    """

    # Prefixos comuns em que um DOI pode vir embrulhado (URL
    # resolver, esquema "doi:") -- normalizados antes de comparar,
    # já que o mesmo DOI pode chegar formatado de jeitos diferentes
    # conforme a fonte que o devolveu.
    _URL_PREFIXES = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi.org/",
    )
    _SCHEME_PREFIX = "doi:"

    # Ordem de preferência para escolher o registro "primário" de
    # um grupo duplicado (o que empresta title/authors/etc. quando
    # mais de uma fonte tem o campo preenchido) -- arbitrária entre
    # fontes igualmente confiáveis, só para tornar a fusão
    # determinística. Fontes fora desta lista (novas, futuras) vão
    # para o fim, sem erro.
    SOURCE_PRIORITY = (
        SourceType.CROSSREF.value,
        SourceType.PUBMED.value,
        SourceType.SEMANTIC_SCHOLAR.value,
    )

    # Campos em que um registro secundário pode completar o que
    # falta no primário durante a fusão.
    _FILLABLE_FIELDS = (
        "title",
        "authors",
        "abstract",
        "publication_date",
        "journal",
        "url",
    )

    def __init__(self):
        self._resolutions = 0

    # ==========================================================
    # 1. NORMALIZAÇÃO DE DOI
    # ==========================================================

    @classmethod
    def normalize(cls, doi: Optional[str]) -> Optional[str]:
        """
        Reduz um DOI ao seu identificador canônico: sem prefixo de
        URL/esquema, sem espaços nem barra final, em minúsculas
        (DOIs são case-insensitive por registro; minúsculas é a
        forma recomendada pelo CrossRef para comparação).

        Devolve None para entradas vazias ou não-string -- "sem
        DOI" é um estado válido, não um erro (nem todo registro
        de literatura tem um).
        """
        if not doi or not isinstance(doi, str):
            return None

        value = doi.strip()
        if not value:
            return None

        lowered = value.lower()
        for prefix in cls._URL_PREFIXES:
            if lowered.startswith(prefix):
                value = value[len(prefix):]
                lowered = value.lower()
                break
        if lowered.startswith(cls._SCHEME_PREFIX):
            value = value[len(cls._SCHEME_PREFIX):]

        value = value.strip().strip("/")
        return value.lower() or None

    # ==========================================================
    # 2. RESOLUÇÃO / DESDUPLICAÇÃO
    # ==========================================================

    def resolve(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Agrupa `records` (no formato canônico de
        SourceConnector._build_record, de uma ou mais fontes) pelo
        DOI normalizado e funde cada grupo com mais de um registro
        em um único registro canônico.

        Registros sem DOI (após normalização) não são agrupados
        entre si -- não há como confirmar que são o mesmo trabalho
        só por isso -- e voltam inalterados em `records`, ao final
        da lista, na ordem em que chegaram.
        """
        groups: Dict[str, List[Dict[str, Any]]] = {}
        without_doi: List[Dict[str, Any]] = []

        for record in records:
            doi = self.normalize(record.get("doi"))
            if doi is None:
                without_doi.append(record)
                continue
            groups.setdefault(doi, []).append(record)

        resolved: List[Dict[str, Any]] = []
        duplicates_removed = 0

        for doi, group in groups.items():
            if len(group) == 1:
                resolved.append(group[0])
            else:
                resolved.append(self._merge(doi, group))
                duplicates_removed += len(group) - 1

        self._resolutions += 1

        return {
            "records": resolved + without_doi,
            "unique_dois": len(resolved),
            "without_doi_count": len(without_doi),
            "duplicates_removed": duplicates_removed,
            "total_in": len(records),
        }

    # ==========================================================
    # 3. FUSÃO DE DUPLICADOS
    # ==========================================================

    def _merge(self, doi: str, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Funde um grupo de registros com o mesmo DOI em um único
        registro canônico -- o registro do topo de SOURCE_PRIORITY
        empresta a base (source/raw/etc.), completado pelos campos
        vazios com o que as demais fontes têm, sem descartar de
        qual fonte cada uma veio (`merged_sources`, `raw_by_source`
        -- rastreabilidade completa mesmo depois da fusão).
        """
        ordered = sorted(group, key=lambda r: self._priority_index(r.get("source")))
        primary = ordered[0]

        merged = dict(primary)
        merged["doi"] = doi

        for other in ordered[1:]:
            for field in self._FILLABLE_FIELDS:
                if not merged.get(field) and other.get(field):
                    merged[field] = other[field]

        merged["merged_sources"] = [r.get("source") for r in ordered]
        merged["raw_by_source"] = {r.get("source"): r.get("raw", {}) for r in ordered}

        return merged

    @classmethod
    def _priority_index(cls, source: Optional[str]) -> int:
        try:
            return cls.SOURCE_PRIORITY.index(source)
        except ValueError:
            return len(cls.SOURCE_PRIORITY)

    # ==========================================================
    # CONSULTAS / OBSERVABILIDADE
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Métricas de uso deste resolvedor."""
        return {"resolutions_performed": self._resolutions}

    def __repr__(self) -> str:
        return f"DOIResolver(resolutions={self._resolutions})"
