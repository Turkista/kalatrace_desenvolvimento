"""
KALATRACE Acquisition -- API Client (infraestrutura HTTP compartilhada)

Implementa a parte de acquisition/__init__.py descrita como
"infraestrutura HTTP/auth compartilhada entre os clientes de fonte"
(source_connector.py, api_client.py). Usado por pubmed_connector.py,
crossref_client.py e semantic_scholar.py -- nenhum dos três fala
com `requests` diretamente; todos passam por este módulo.

Responsabilidades deste módulo, e só estas:

- montar a URL e executar a chamada HTTP (GET);
- aplicar um intervalo mínimo educado entre chamadas
  (min_interval_seconds), já que as 3 fontes cobertas aqui
  (PubMed/NCBI, CrossRef, Semantic Scholar) documentam limites de
  requisições por segundo para uso não-autenticado;
- tentar de novo, com backoff exponencial, falhas transitórias
  (timeout, erro de conexão, HTTP 429, HTTP 5xx) até
  `max_retries`;
- converter falhas em exceções próprias do domínio de aquisição
  (SourceUnavailableError, SourceRateLimitError,
  SourceResponseError), para que os clientes de fonte e quem os
  chama não precisem depender de `requests` para tratar erro.

NÃO faz parte deste módulo: interpretar o conteúdo da resposta
(cada fonte tem formato próprio -- XML no PubMed, JSON no CrossRef
e no Semantic Scholar) nem decidir o que fazer com uma falha (isso
é do chamador). Ver source_connector.py para o contrato comum
acima desta camada.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import requests


# ==========================================================
# Exceções do domínio de aquisição
# ==========================================================


class SourceUnavailableError(Exception):
    """
    Fonte externa não respondeu de forma utilizável: timeout,
    erro de conexão, ou HTTP 5xx persistente após todas as
    tentativas permitidas.
    """


class SourceRateLimitError(Exception):
    """
    Fonte externa recusou a chamada por limite de requisições
    (HTTP 429) mesmo após todas as tentativas permitidas.
    """


class SourceResponseError(Exception):
    """
    Fonte externa respondeu, mas com um erro do lado do cliente
    (HTTP 4xx diferente de 429) ou com um corpo que não é o
    formato esperado (ex.: JSON inválido onde JSON era esperado).
    Repetir a mesma chamada não deve mudar o resultado, por isso
    não é tentada de novo.
    """


# ==========================================================
# API Client
# ==========================================================


class APIClient:
    """
    Cliente HTTP genérico e educado, compartilhado pelos 3
    clientes de fonte de literatura externa.

    Cada cliente de fonte (PubMedConnector, CrossrefClient,
    SemanticScholarClient) cria sua própria instância de
    APIClient, com o base_url, headers e min_interval_seconds
    apropriados para os limites documentados daquela fonte --
    este módulo não conhece nenhuma fonte específica.
    """

    DEFAULT_TIMEOUT_SECONDS = 15.0
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_SECONDS = 1.0

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        min_interval_seconds: float = 0.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.min_interval_seconds = max(0.0, min_interval_seconds)
        self.max_retries = max(0, max_retries)
        self.backoff_seconds = backoff_seconds

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "KALATRACE-Acquisition/1.0 "
                "(+https://github.com/kalatrace; camada de "
                "aquisicao de literatura cientifica)",
            }
        )
        if headers:
            self.session.headers.update(headers)

        self._last_request_at: Optional[float] = None

    # ==========================================================
    # RATE LIMITING (politeness entre chamadas à mesma fonte)
    # ==========================================================

    def _respect_rate_limit(self) -> None:
        if self.min_interval_seconds <= 0 or self._last_request_at is None:
            return
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)

    # ==========================================================
    # RETRY / BACKOFF
    # ==========================================================

    def _retry_or_raise(
        self, attempt: int, error: Exception, cause: Optional[Exception]
    ) -> None:
        """
        Decide entre esperar e tentar de novo (retorna normalmente)
        ou desistir (levanta `error`), conforme `attempt` já
        excedeu `max_retries`.
        """
        if attempt > self.max_retries:
            raise error from cause
        time.sleep(self.backoff_seconds * (2 ** (attempt - 1)))

    # ==========================================================
    # GET
    # ==========================================================

    def _build_url(self, path: str) -> str:
        if not path:
            return self.base_url
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(
        self,
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> requests.Response:
        """
        GET com rate limiting e retry/backoff já aplicados.
        Levanta SourceUnavailableError, SourceRateLimitError ou
        SourceResponseError em vez de deixar vazar exceções de
        `requests`.
        """
        url = self._build_url(path)
        attempt = 0

        while True:
            attempt += 1
            self._respect_rate_limit()
            self._last_request_at = time.monotonic()

            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout_seconds or self.timeout_seconds,
                )
            except requests.Timeout as exc:
                self._retry_or_raise(
                    attempt,
                    SourceUnavailableError(f"timeout ao consultar {url}"),
                    exc,
                )
                continue
            except requests.ConnectionError as exc:
                self._retry_or_raise(
                    attempt,
                    SourceUnavailableError(f"falha de conexão com {url}"),
                    exc,
                )
                continue

            if response.status_code == 429:
                self._retry_or_raise(
                    attempt,
                    SourceRateLimitError(
                        f"limite de requisições excedido em {url}"
                    ),
                    None,
                )
                continue

            if 500 <= response.status_code < 600:
                self._retry_or_raise(
                    attempt,
                    SourceUnavailableError(
                        f"{url} respondeu HTTP {response.status_code}"
                    ),
                    None,
                )
                continue

            if 400 <= response.status_code < 500:
                # erro do lado do cliente (query malformada, id
                # inexistente, etc.) -- repetir não muda o resultado
                raise SourceResponseError(
                    f"{url} respondeu HTTP {response.status_code}: "
                    f"{response.text[:300]}"
                )

            return response

    # ==========================================================
    # ATALHOS DE FORMATO
    # ==========================================================

    def get_json(
        self,
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """GET que já espera e decodifica um corpo JSON."""
        response = self.get(
            path, params=params, headers=headers, timeout_seconds=timeout_seconds
        )
        try:
            return response.json()
        except ValueError as exc:
            raise SourceResponseError(
                f"resposta de {response.url} não é JSON válido"
            ) from exc

    def get_text(
        self,
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> str:
        """GET que devolve o corpo como texto bruto (ex.: XML)."""
        response = self.get(
            path, params=params, headers=headers, timeout_seconds=timeout_seconds
        )
        return response.text

    def __repr__(self) -> str:
        return f"APIClient(base_url={self.base_url!r})"
