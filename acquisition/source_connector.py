"""
KALATRACE Acquisition -- Source Connector (contrato comum das fontes)

Contrato compartilhado pelos 3 clientes de fonte de literatura
externa já nomeados no DOCUMENTO 23, Seção 11
(pubmed_connector.py, crossref_client.py, semantic_scholar.py).

O DOCUMENTO 23 descreve, separadamente:

    ScientificSearchEngine -> localizar literatura relevante
    LiteratureRetriever     -> obter metadados/conteúdo
                               autorizado de um registro já
                               identificado

Cada cliente concreto cobre os dois papéis para sua fonte
(search / fetch_by_id) -- não há uma classe por papel, pelo mesmo
motivo já registrado em engines/scientific_research/__init__.py
para ScientificResearchEngine: a distinção é conceitual, não uma
fronteira que precise de objetos separados por fonte.

NÃO faz parte deste contrato (fora do escopo desta camada):

- desduplicar/resolver o mesmo trabalho entre fontes diferentes
  por DOI -- isso é doi_resolver.py, ainda não implementado;
- interpretar objetivo/metodologia/resultados/mecanismos de um
  texto completo -- isso é ArticleParser (document_loader.py e os
  readers por formato), ainda não implementado;
- decidir se um resultado vira IEC, ou julgar sustentação
  científica -- isso é responsabilidade de camadas posteriores do
  fluxo (Seção 10: Contextualização, Comparação, Validação).

Toda implementação concreta devolve registros no mesmo formato
canônico (ver _build_record), para que um futuro
acquisition_pipeline.py possa combinar resultados das 3 fontes sem
precisar saber, campo a campo, de qual fonte cada um veio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from shared.enums import AcquisitionStatus, SourceType
from acquisition.api_client import (
    APIClient,
    SourceRateLimitError,
    SourceResponseError,
    SourceUnavailableError,
)

__all__ = [
    "SourceConnector",
    "SourceUnavailableError",
    "SourceRateLimitError",
    "SourceResponseError",
]


class SourceConnector(ABC):
    """
    Classe-base de todo cliente de fonte de literatura externa.

    Subclasses concretas (PubMedConnector, CrossrefClient,
    SemanticScholarClient) definem `source_type` e implementam
    `search`/`fetch_by_id`; esta classe cuida do que é comum às
    três: rastreamento de status (AcquisitionStatus), contadores,
    último erro, e a montagem do registro normalizado que todas
    devolvem no mesmo formato.
    """

    #: Definido por cada subclasse concreta (ex.: SourceType.PUBMED)
    source_type: SourceType

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.status: AcquisitionStatus = AcquisitionStatus.INITIALIZED
        self._last_error: Optional[str] = None
        self._search_count = 0
        self._fetch_count = 0
        self._error_count = 0

    # ==========================================================
    # CONTRATO -- implementado por cada fonte concreta
    # ==========================================================

    @abstractmethod
    def search(
        self, query: str, max_results: int = 20, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Localiza literatura relevante para `query` nesta fonte
        (papel de ScientificSearchEngine, Seção 11). Devolve uma
        lista de registros normalizados (ver _build_record).
        """

    @abstractmethod
    def fetch_by_id(self, external_id: str) -> Dict[str, Any]:
        """
        Obtém metadados completos de um registro já identificado
        nesta fonte, pelo id nativo dela (papel de
        LiteratureRetriever, Seção 11). Devolve um único registro
        normalizado (ver _build_record).
        """

    # ==========================================================
    # NORMALIZAÇÃO -- formato comum entre as 3 fontes
    # ==========================================================

    def _build_record(
        self,
        external_id: Optional[str],
        title: Optional[str],
        authors: Optional[List[str]] = None,
        abstract: Optional[str] = None,
        doi: Optional[str] = None,
        publication_date: Optional[str] = None,
        journal: Optional[str] = None,
        url: Optional[str] = None,
        raw: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Monta um registro de literatura no formato canônico usado
        pelas 3 fontes -- o que doi_resolver.py e o futuro
        IECBuilder vão consumir, sem precisar saber de qual fonte
        cada registro veio.

        `raw` preserva a resposta original da fonte (ou o trecho
        relevante dela) -- rastreabilidade completa da origem
        (DOCUMENTO 23, Seção 4), mesmo depois da normalização.
        """
        return {
            "source": self.source_type.value,
            "external_id": str(external_id) if external_id else None,
            "title": (title or "").strip(),
            "authors": authors or [],
            "abstract": abstract,
            "doi": doi.strip().lower() if isinstance(doi, str) and doi else None,
            "publication_date": publication_date,
            "journal": journal,
            "url": url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "raw": raw or {},
        }

    # ==========================================================
    # RASTREAMENTO DE STATUS (AcquisitionStatus)
    # ==========================================================
    #
    # Helpers que cada subclasse usa em volta das próprias chamadas
    # HTTP -- nunca engolem a exceção original, só registram o
    # estado antes de deixá-la subir (rastreabilidade de falha,
    # mesmo princípio de ManualAcquisition: nunca julgamento
    # silencioso).

    def _begin(self, status: AcquisitionStatus = AcquisitionStatus.RETRIEVING) -> None:
        self.status = status

    def _succeed(self) -> None:
        self.status = AcquisitionStatus.COMPLETED

    def _fail(self, error: Exception) -> None:
        self.status = AcquisitionStatus.FAILED
        self._last_error = str(error)
        self._error_count += 1

    # ==========================================================
    # CONSULTAS / OBSERVABILIDADE
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Métricas de uso deste cliente de fonte."""
        return {
            "source": self.source_type.value,
            "status": self.status.value,
            "searches_performed": self._search_count,
            "fetches_performed": self._fetch_count,
            "errors": self._error_count,
            "last_error": self._last_error,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Verifica se este cliente de fonte está íntegro (não
        necessariamente se a fonte externa está no ar agora --
        isso só se sabe tentando uma chamada real).
        """
        return {
            "source": self.source_type.value,
            "status": self.status.value,
            "api_client_connected": self.api_client is not None,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"source={self.source_type.value}, status={self.status.value})"
        )
