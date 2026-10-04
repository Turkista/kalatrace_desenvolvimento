"""
KALATRACE Acquisition -- CrossRef Client

Cliente de fonte para o CrossRef (DOCUMENTO 23, Seção 11), um dos 3
clientes de fonte já nomeados lá. Implementa SourceConnector usando
a REST API pública do CrossRef (https://api.crossref.org):

    GET /works?query=...   -> localizar trabalhos relevantes
                               (papel de ScientificSearchEngine)
    GET /works/{doi}        -> obter metadados completos de um DOI
                               já conhecido (papel de
                               LiteratureRetriever)

O CrossRef documenta uma "polite pool" com limites de requisição
melhores para quem se identifica com um `mailto` no header
User-Agent -- por isso `mailto` é aceito no construtor (ou via
CROSSREF_MAILTO no ambiente) e incluído no User-Agent da sessão
HTTP, não autenticação de verdade.

NÃO faz parte deste cliente: desduplicar por DOI entre fontes
(doi_resolver.py) nem interpretar o texto completo do artigo (o
CrossRef, de qualquer forma, só devolve metadados bibliográficos,
não o texto completo) -- ver acquisition/__init__.py e
source_connector.py.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from shared.enums import SourceType
from acquisition.api_client import APIClient
from acquisition.source_connector import SourceConnector


class CrossrefClient(SourceConnector):
    """
    Cliente de fonte para o CrossRef via sua REST API pública.

    Uso:
        crossref = CrossrefClient(mailto="pesquisa@exemplo.org")
        resultados = crossref.search("crispr cardiac regeneration", max_results=10)
        registro = crossref.fetch_by_id("10.1038/s41586-020-2649-2")
    """

    source_type = SourceType.CROSSREF

    BASE_URL = "https://api.crossref.org"

    # CrossRef não documenta um limite fixo, mas recomenda ritmo
    # moderado mesmo na polite pool -- 0.1s (10 req/s) é
    # conservador o bastante para não ser bloqueado.
    DEFAULT_MIN_INTERVAL_SECONDS = 0.1

    def __init__(
        self,
        mailto: Optional[str] = None,
        api_client: Optional[APIClient] = None,
    ):
        """
        mailto: se omitido, tenta CROSSREF_MAILTO no ambiente antes
        de seguir sem ele (a API funciona sem, fora da polite pool).
        """
        self.mailto = mailto or os.getenv("CROSSREF_MAILTO")

        headers = {}
        if self.mailto:
            headers["User-Agent"] = (
                f"KALATRACE-Acquisition/1.0 (mailto:{self.mailto})"
            )

        client = api_client or APIClient(
            base_url=self.BASE_URL,
            headers=headers or None,
            min_interval_seconds=self.DEFAULT_MIN_INTERVAL_SECONDS,
        )
        super().__init__(client)

    # ==========================================================
    # 1. SEARCH (ScientificSearchEngine) -- GET /works
    # ==========================================================

    def search(
        self, query: str, max_results: int = 20, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        self._begin()
        try:
            params: Dict[str, Any] = {"query": query, "rows": max_results}
            if self.mailto:
                params["mailto"] = self.mailto

            response = self.api_client.get_json("works", params=params)
            items = response.get("message", {}).get("items", [])
            records = [self._parse_work(item) for item in items]

            self._search_count += 1
            self._succeed()
            return records
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # 2. FETCH_BY_ID (LiteratureRetriever) -- GET /works/{doi}
    # ==========================================================

    def fetch_by_id(self, external_id: str) -> Dict[str, Any]:
        """`external_id` é o DOI do trabalho (ex.: "10.1038/...")."""
        self._begin()
        try:
            params = {"mailto": self.mailto} if self.mailto else None
            response = self.api_client.get_json(
                f"works/{external_id}", params=params
            )
            record = self._parse_work(response.get("message", {}))

            self._fetch_count += 1
            self._succeed()
            return record
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # PARSING
    # ==========================================================

    def _parse_work(self, item: Dict[str, Any]) -> Dict[str, Any]:
        doi = item.get("DOI")

        titles = item.get("title") or []
        title = titles[0] if titles else ""

        authors = []
        for author in item.get("author") or []:
            given = author.get("given")
            family = author.get("family")
            name = author.get("name")  # entidades coletivas
            if family:
                authors.append(f"{given} {family}".strip() if given else family)
            elif name:
                authors.append(name)

        abstract = item.get("abstract")  # às vezes vem como JATS XML

        container_titles = item.get("container-title") or []
        journal = container_titles[0] if container_titles else None

        publication_date = self._parse_date_parts(item)

        url = item.get("URL")

        return self._build_record(
            external_id=doi,
            title=title,
            authors=authors,
            abstract=abstract,
            doi=doi,
            publication_date=publication_date,
            journal=journal,
            url=url,
            raw={"type": item.get("type"), "publisher": item.get("publisher")},
        )

    @staticmethod
    def _parse_date_parts(item: Dict[str, Any]) -> Optional[str]:
        for key in ("published-print", "published-online", "published", "issued"):
            date_field = item.get(key)
            if not date_field:
                continue
            date_parts = date_field.get("date-parts")
            if date_parts and date_parts[0]:
                parts = [str(part) for part in date_parts[0] if part is not None]
                if parts:
                    return "-".join(parts)
        return None
