"""
KALATRACE Acquisition -- Semantic Scholar Client

Cliente de fonte para o Semantic Scholar (DOCUMENTO 23, Seção 11),
um dos 3 clientes de fonte já nomeados lá. Implementa
SourceConnector usando a Semantic Scholar Academic Graph API
(https://api.semanticscholar.org/graph/v1):

    GET /paper/search       -> localizar trabalhos relevantes
                                (papel de ScientificSearchEngine)
    GET /paper/{paper_id}   -> obter metadados completos de um
                                trabalho já identificado (papel de
                                LiteratureRetriever)

Sem chave de API, o Semantic Scholar aplica um limite de
requisições mais restrito (documentado como compartilhado entre
todo tráfego não autenticado); uma api_key gratuita (cadastro no
próprio site) aumenta esse limite -- por isso min_interval_seconds
já vem menor quando `api_key` é passado.

NÃO faz parte deste cliente: desduplicar por DOI entre fontes
(doi_resolver.py) nem interpretar o texto completo do artigo
(ArticleParser) -- ver acquisition/__init__.py e
source_connector.py.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from shared.enums import SourceType
from acquisition.api_client import APIClient
from acquisition.source_connector import SourceConnector


class SemanticScholarClient(SourceConnector):
    """
    Cliente de fonte para o Semantic Scholar via sua Academic
    Graph API pública.

    Uso:
        s2 = SemanticScholarClient(api_key="...")  # opcional
        resultados = s2.search("crispr cardiac regeneration", max_results=10)
        registro = s2.fetch_by_id(resultados[0]["external_id"])
    """

    source_type = SourceType.SEMANTIC_SCHOLAR

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    # Campos pedidos em toda chamada -- mesmo formato entre search
    # e fetch_by_id, para que _parse_paper sirva às duas.
    FIELDS = "title,abstract,authors,year,venue,externalIds,url"

    # Sem api_key, o limite documentado é bem mais apertado que com
    # uma -- 1.1s é conservador o bastante para não ser bloqueado
    # em uso anônimo; com api_key, 0.1s.
    DEFAULT_MIN_INTERVAL_SECONDS = 1.1
    DEFAULT_MIN_INTERVAL_SECONDS_WITH_KEY = 0.1

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_client: Optional[APIClient] = None,
    ):
        """
        api_key: se omitida, tenta SEMANTIC_SCHOLAR_API_KEY no
        ambiente antes de seguir sem ela (a API funciona sem, com
        limites de requisição mais baixos).
        """
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        headers = {"x-api-key": self.api_key} if self.api_key else None

        client = api_client or APIClient(
            base_url=self.BASE_URL,
            headers=headers,
            min_interval_seconds=(
                self.DEFAULT_MIN_INTERVAL_SECONDS_WITH_KEY
                if self.api_key
                else self.DEFAULT_MIN_INTERVAL_SECONDS
            ),
        )
        super().__init__(client)

    # ==========================================================
    # 1. SEARCH (ScientificSearchEngine) -- GET /paper/search
    # ==========================================================

    def search(
        self, query: str, max_results: int = 20, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        self._begin()
        try:
            params = {
                "query": query,
                "limit": max_results,
                "fields": self.FIELDS,
            }
            response = self.api_client.get_json("paper/search", params=params)
            papers = response.get("data", []) if isinstance(response, dict) else []
            records = [self._parse_paper(paper) for paper in papers]

            self._search_count += 1
            self._succeed()
            return records
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # 2. FETCH_BY_ID (LiteratureRetriever) -- GET /paper/{id}
    # ==========================================================

    def fetch_by_id(self, external_id: str) -> Dict[str, Any]:
        """
        `external_id` é o paperId nativo do Semantic Scholar, mas a
        API também aceita prefixos como "DOI:..." ou "PMID:..." --
        ver documentação de "Paper identifiers" do Semantic Scholar.
        """
        self._begin()
        try:
            params = {"fields": self.FIELDS}
            response = self.api_client.get_json(
                f"paper/{external_id}", params=params
            )
            record = self._parse_paper(response)

            self._fetch_count += 1
            self._succeed()
            return record
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # PARSING
    # ==========================================================

    def _parse_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        paper_id = paper.get("paperId")
        title = paper.get("title") or ""
        abstract = paper.get("abstract")
        journal = paper.get("venue")
        year = paper.get("year")
        url = paper.get("url")

        authors = [
            author.get("name")
            for author in paper.get("authors") or []
            if author.get("name")
        ]

        external_ids = paper.get("externalIds") or {}
        doi = external_ids.get("DOI")

        return self._build_record(
            external_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            doi=doi,
            publication_date=str(year) if year else None,
            journal=journal,
            url=url,
            raw={"externalIds": external_ids},
        )
