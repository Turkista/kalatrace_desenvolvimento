"""
KALATRACE Acquisition -- Acquisition Pipeline

Orquestra o fluxo de aquisição automatizada ponta a ponta
(DOCUMENTO 23, Seção 10: Aquisição -> Normalização -> Construção
de IECs), um dos módulos ainda não implementados listados em
acquisition/__init__.py.

Consome os 3 clientes de fonte já implementados -- PubMedConnector,
CrossrefClient, SemanticScholarClient --, hoje só usáveis
isoladamente (nenhum outro ponto do projeto ainda os chama), e o
DOIResolver para desduplicar entre eles. Cobre:

    Aquisição      -> consulta as 3 fontes em paralelo lógico
                      (uma após a outra; cada uma já tem seu
                      próprio rate limiting em APIClient)
    Normalização   -> já feita por cada cliente em
                      SourceConnector._build_record; este módulo
                      soma os resultados das 3 fontes e aciona o
                      DOIResolver para fundir o mesmo trabalho
                      quando aparece em mais de uma

NÃO faz parte deste módulo (fora do escopo desta camada):

- decidir se um registro vira IEC, ou julgar sustentação
  científica -- isso é responsabilidade de camadas posteriores do
  fluxo (Seção 10: Contextualização, Comparação, Validação; o
  IECBuilder citado na Seção 11 ainda não existe). Este pipeline
  entrega os registros normalizados e deduplicados prontos para
  esse próximo passo, não os promove sozinho;
- interpretar texto completo do artigo (ArticleParser --
  document_loader.py e os readers por formato, ainda não
  implementados) -- os 3 clientes só cobrem metadados/resumo.

Falha de uma fonte não derruba as demais: cada fonte já registra
seu próprio erro internamente (SourceConnector._fail, nunca
silencioso), mas aqui, no nível da orquestração entre fontes
independentes, uma falha isolada não deve impedir que as outras
duas contribuam com o que conseguiram -- por isso o erro de cada
fonte é capturado e devolvido em `sources_failed`, nunca engolido.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from acquisition.crossref_client import CrossrefClient
from acquisition.doi_resolver import DOIResolver
from acquisition.pubmed_connector import PubMedConnector
from acquisition.semantic_scholar import SemanticScholarClient
from acquisition.source_connector import SourceConnector

__all__ = ["AcquisitionPipeline"]


class AcquisitionPipeline:
    """
    Orquestra os 3 clientes de fonte de literatura + o DOIResolver.

    Uso:
        pipeline = AcquisitionPipeline()
        resultado = pipeline.run("crispr cardiac regeneration", max_results_per_source=10)
        registros = resultado["records"]
    """

    def __init__(
        self,
        connectors: Optional[List[SourceConnector]] = None,
        doi_resolver: Optional[DOIResolver] = None,
    ):
        """
        connectors: se omitido, instancia as 3 fontes já nomeadas
        no DOCUMENTO 23 com a configuração padrão de cada uma
        (credenciais/mailto/api_key lidos do ambiente por cada
        cliente, como já documentado em cada um deles). Aceita uma
        lista customizada -- inclusive com um subconjunto das 3,
        ou instâncias já configuradas com credenciais explícitas.
        """
        self.connectors: List[SourceConnector] = (
            list(connectors)
            if connectors is not None
            else [PubMedConnector(), CrossrefClient(), SemanticScholarClient()]
        )
        self.doi_resolver = doi_resolver or DOIResolver()
        self._runs = 0

    # ==========================================================
    # 1. AQUISIÇÃO -- consulta as 3 fontes
    # ==========================================================

    def search_all(
        self, query: str, max_results_per_source: int = 20, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Consulta `query` em cada fonte configurada e soma os
        registros normalizados obtidos. Não deduplica -- isso é
        `run()`, que chama este método e depois aciona o
        DOIResolver.

        Uma fonte que falhar não impede as demais de contribuir:
        o erro é registrado em `errors` (chave = source_type),
        nunca silenciado nem repassado como exceção que
        interromperia as outras.
        """
        records: List[Dict[str, Any]] = []
        errors: Dict[str, str] = {}

        for connector in self.connectors:
            source_name = connector.source_type.value
            try:
                results = connector.search(
                    query, max_results=max_results_per_source, **kwargs
                )
                records.extend(results)
            except Exception as exc:
                errors[source_name] = str(exc)

        return {"records": records, "errors": errors}

    # ==========================================================
    # 2. FLUXO COMPLETO -- Aquisição -> Normalização (dedup)
    # ==========================================================

    def run(
        self,
        query: str,
        max_results_per_source: int = 20,
        resolve_duplicates: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Executa o fluxo de aquisição ponta a ponta para `query`:
        consulta as 3 fontes (search_all) e, se
        `resolve_duplicates` (padrão), funde o mesmo trabalho
        encontrado em mais de uma fonte via DOIResolver.

        Devolve os registros normalizados e deduplicados,
        acompanhados de métricas do que foi consultado, o que
        falhou e quantos duplicados foram removidos -- prontos
        para o próximo passo do fluxo (Seção 10: Contextualização,
        Comparação, Validação), que este pipeline não realiza.
        """
        self._runs += 1
        acquired = self.search_all(query, max_results_per_source, **kwargs)
        records = acquired["records"]

        if resolve_duplicates and records:
            resolution = self.doi_resolver.resolve(records)
            final_records = resolution["records"]
            duplicates_removed = resolution["duplicates_removed"]
        else:
            final_records = records
            duplicates_removed = 0

        return {
            "query": query,
            "records": final_records,
            "total_retrieved": len(records),
            "total_after_dedup": len(final_records),
            "duplicates_removed": duplicates_removed,
            "sources_queried": [c.source_type.value for c in self.connectors],
            "sources_failed": acquired["errors"],
        }

    # ==========================================================
    # CONSULTAS / OBSERVABILIDADE
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Métricas agregadas deste pipeline e de cada fonte que orquestra."""
        return {
            "runs": self._runs,
            "connectors": [c.stats() for c in self.connectors],
            "doi_resolver": self.doi_resolver.stats(),
        }

    def health_check(self) -> Dict[str, Any]:
        """Saúde de cada fonte orquestrada por este pipeline."""
        return {c.source_type.value: c.health_check() for c in self.connectors}

    def __repr__(self) -> str:
        sources = [c.source_type.value for c in self.connectors]
        return f"AcquisitionPipeline(sources={sources}, runs={self._runs})"
