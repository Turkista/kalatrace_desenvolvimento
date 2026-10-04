"""
KALATRACE Acquisition -- PubMed Connector

Cliente de fonte para o PubMed/NCBI (DOCUMENTO 23, Seção 11), um
dos 3 clientes de fonte já nomeados lá. Implementa SourceConnector
usando a API pública E-utilities do NCBI:

    esearch.fcgi -> localizar PMIDs relevantes para uma busca
                    (papel de ScientificSearchEngine)
    efetch.fcgi  -> obter os metadados completos (título, autores,
                    resumo, periódico, data, DOI) desses PMIDs
                    (papel de LiteratureRetriever)

Sem chave de API, o NCBI recomenda no máximo 3 requisições/segundo;
com uma api_key (gratuita, cadastro em conta NCBI), o limite sobe
para 10/segundo -- por isso min_interval_seconds já vem menor
quando `api_key` é passado. `email`/`tool` são parâmetros que o
NCBI pede para uso educado da API (identificação de quem está
consultando), não autenticação.

NÃO faz parte deste cliente: desduplicar por DOI entre fontes
(doi_resolver.py) nem interpretar o texto completo do artigo além
do resumo (ArticleParser) -- ver acquisition/__init__.py e
source_connector.py.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from shared.enums import SourceType
from acquisition.api_client import APIClient
from acquisition.source_connector import SourceConnector


class PubMedConnector(SourceConnector):
    """
    Cliente de fonte para o PubMed/NCBI via E-utilities.

    Uso:
        pubmed = PubMedConnector(email="pesquisa@exemplo.org")
        resultados = pubmed.search("crispr cardiac regeneration", max_results=10)
        registro = pubmed.fetch_by_id(resultados[0]["external_id"])
    """

    source_type = SourceType.PUBMED

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    # Sem api_key: NCBI recomenda até 3 req/s -- 0.34s de intervalo
    # é uma margem segura. Com api_key: até 10 req/s.
    DEFAULT_MIN_INTERVAL_SECONDS = 0.34
    DEFAULT_MIN_INTERVAL_SECONDS_WITH_KEY = 0.11

    def __init__(
        self,
        email: Optional[str] = None,
        tool: str = "KALATRACE",
        api_key: Optional[str] = None,
        api_client: Optional[APIClient] = None,
    ):
        """
        email/api_key: se omitidos, tenta as variáveis de ambiente
        NCBI_EMAIL e NCBI_API_KEY antes de seguir sem elas (a API
        funciona sem, só com limites de requisição mais baixos).
        """
        self.email = email or os.getenv("NCBI_EMAIL")
        self.tool = tool
        self.api_key = api_key or os.getenv("NCBI_API_KEY")

        client = api_client or APIClient(
            base_url=self.BASE_URL,
            min_interval_seconds=(
                self.DEFAULT_MIN_INTERVAL_SECONDS_WITH_KEY
                if self.api_key
                else self.DEFAULT_MIN_INTERVAL_SECONDS
            ),
        )
        super().__init__(client)

    # ==========================================================
    # PARÂMETROS COMUNS (identificação educada exigida pelo NCBI)
    # ==========================================================

    def _common_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {"tool": self.tool}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    # ==========================================================
    # 1. SEARCH (ScientificSearchEngine) -- esearch.fcgi
    # ==========================================================

    def search(
        self, query: str, max_results: int = 20, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Localiza PMIDs relevantes para `query` e devolve os
        registros já com metadados completos (esearch + efetch em
        sequência, como a maioria dos consumidores desta API
        precisa).
        """
        self._begin()
        try:
            params = {
                **self._common_params(),
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
            }
            search_result = self.api_client.get_json("esearch.fcgi", params=params)
            pmids = (
                search_result.get("esearchresult", {}).get("idlist", [])
                if isinstance(search_result, dict)
                else []
            )

            records: List[Dict[str, Any]] = []
            if pmids:
                records = self._fetch_records(pmids)

            self._search_count += 1
            self._succeed()
            return records
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # 2. FETCH_BY_ID (LiteratureRetriever) -- efetch.fcgi
    # ==========================================================

    def fetch_by_id(self, external_id: str) -> Dict[str, Any]:
        """Obtém os metadados completos de um único PMID."""
        self._begin()
        try:
            records = self._fetch_records([external_id])
            if not records:
                raise ValueError(f"PMID {external_id} não encontrado no PubMed")

            self._fetch_count += 1
            self._succeed()
            return records[0]
        except Exception as exc:
            self._fail(exc)
            raise

    # ==========================================================
    # EFETCH + PARSING (compartilhado por search e fetch_by_id)
    # ==========================================================

    def _fetch_records(self, pmids: List[str]) -> List[Dict[str, Any]]:
        params = {
            **self._common_params(),
            "db": "pubmed",
            "id": ",".join(str(pmid) for pmid in pmids),
            "retmode": "xml",
            "rettype": "abstract",
        }
        xml_text = self.api_client.get_text("efetch.fcgi", params=params)
        return self._parse_pubmed_xml(xml_text)

    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_text)
        records: List[Dict[str, Any]] = []
        for article in root.findall(".//PubmedArticle"):
            records.append(self._parse_article(article))
        return records

    def _parse_article(self, article: ET.Element) -> Dict[str, Any]:
        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else None

        title_el = article.find(".//ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""

        abstract_parts = [
            "".join(el.itertext()).strip()
            for el in article.findall(".//Abstract/AbstractText")
        ]
        abstract = " ".join(part for part in abstract_parts if part) or None

        authors = []
        for author_el in article.findall(".//AuthorList/Author"):
            last_name = author_el.findtext("LastName")
            initials = author_el.findtext("Initials")
            collective_name = author_el.findtext("CollectiveName")
            if last_name:
                authors.append(
                    f"{last_name} {initials}".strip() if initials else last_name
                )
            elif collective_name:
                authors.append(collective_name)

        journal = article.findtext(".//Journal/Title")

        publication_date = self._parse_pub_date(article)

        doi = None
        for id_el in article.findall(".//ArticleIdList/ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text
                break

        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None

        return self._build_record(
            external_id=pmid,
            title=title,
            authors=authors,
            abstract=abstract,
            doi=doi,
            publication_date=publication_date,
            journal=journal,
            url=url,
            raw={"pmid": pmid},
        )

    @staticmethod
    def _parse_pub_date(article: ET.Element) -> Optional[str]:
        pub_date_el = article.find(".//Journal/JournalIssue/PubDate")
        if pub_date_el is None:
            return None

        year = pub_date_el.findtext("Year")
        month = pub_date_el.findtext("Month")
        day = pub_date_el.findtext("Day")

        if not year:
            medline_date = pub_date_el.findtext("MedlineDate")
            return medline_date

        parts = [part for part in (year, month, day) if part]
        return "-".join(parts)
