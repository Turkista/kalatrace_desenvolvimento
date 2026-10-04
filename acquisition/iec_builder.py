"""
KALATRACE Acquisition -- IEC Builder

Converte o que os módulos de aquisição capturam/coletam em IECs de
verdade (DOCUMENTO 23, Seção 11, o módulo citado em todo o resto de
acquisition/ como "ainda não implementado" até agora):

    ManualAcquisition.capture()          -> build_from_manual_capture
    AcquisitionPipeline.run()["records"] -> build_from_acquisition_record /
                                             build_many_from_acquisition

Em ambos os casos o construtor real de IEC continua sendo
engines.base.base_engine.CoreEngine.create_iec (documentado lá como
"Ponto único de criação de conhecimento no sistema") -- este módulo
não o substitui, só decide *como* transformar um registro de
aquisição estruturalmente íntegro nos argumentos que esse construtor
espera, preservando rastreabilidade completa de origem (DOCUMENTO 23,
Seção 4) dentro de `iec.metadata` (na prática `iec.properties`,
herdado de graph.base.node.Node).

Como os demais módulos de aquisição, o IECBuilder:

- NÃO julga mérito científico -- só valida integridade estrutural
  (campos obrigatórios presentes e não vazios), mesmo padrão de
  ManualAcquisition._validate_integrity;
- NÃO escreve no grafo sozinho -- devolve o(s) IEC(s) construído(s);
  quem chama decide se/quando faz graph.add_node(iec) e roda
  inferência (mesma composição que POST /iec já faz na API, e que
  os novos endpoints /acquisition/search-and-build e
  /acquisition/build-iecs em api/main.py reaproveitam).
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from engines.base.base_engine import CoreEngine

__all__ = ["IECBuilder"]


class IECBuilder:
    """
    Constrói IECs a partir de registros de aquisição (manual ou
    automatizada).

    Uso:
        builder = IECBuilder()
        iec = builder.build_from_acquisition_record(record)
        # ou, em lote, resiliente a registros malformados:
        iecs = builder.build_many_from_acquisition(records)
    """

    def __init__(self, engine: Optional[CoreEngine] = None):
        self.engine = engine or CoreEngine()
        self.built_count = 0
        self.skipped: List[Dict[str, Any]] = []

    # ==========================================================
    # 1. A PARTIR DE CAPTURA MANUAL (ManualAcquisition.capture())
    # ==========================================================

    def build_from_manual_capture(
        self,
        capture: Dict[str, Any],
        node_type: Optional[str] = None,
    ) -> Any:
        """
        Constrói uma IEC a partir de 1 registro de
        ManualAcquisition.capture() (chaves: capture_id, statement,
        submitted_by, submission_type, metadata, status, captured_at).

        O id da IEC é derivado do capture_id (`IEC-{capture_id}`),
        para que a rastreabilidade entre a submissão bruta e a IEC
        que ela originou fique explícita nos dois sentidos -- o
        chamador ainda deve registrar isso do lado da captura via
        ManualAcquisition.mark_promoted(capture_id, iec.id), este
        método não chama isso sozinho (não tem a instância do
        ManualAcquisition que produziu a captura).
        """
        self._require_fields(capture, ("capture_id", "statement", "submitted_by"), origin="manual_capture")

        iec_id = f"IEC-{capture['capture_id']}"

        metadata = {
            "title": capture["statement"][:120],
            "origin": "manual_acquisition",
            "capture_id": capture["capture_id"],
            "submitted_by": capture["submitted_by"],
            "submission_type": capture.get("submission_type"),
            "captured_at": capture.get("captured_at"),
        }
        extra = capture.get("metadata") or {}
        metadata.update(extra)

        iec = self.engine.create_iec(
            id=iec_id,
            content=capture["statement"],
            node_type=node_type or capture.get("submission_type") or "Conhecimento",
            metadata=metadata,
        )
        self.built_count += 1
        return iec

    # ==========================================================
    # 2. A PARTIR DE 1 REGISTRO DE LITERATURA (PubMed/CrossRef/
    #    Semantic Scholar, via SourceConnector/AcquisitionPipeline)
    # ==========================================================

    def build_from_acquisition_record(
        self,
        record: Dict[str, Any],
        node_type: str = "Literatura Científica",
    ) -> Any:
        """
        Constrói uma IEC a partir de 1 registro normalizado de
        literatura externa (formato de SourceConnector._build_record,
        já deduplicado por DOI ou não -- ver acquisition/doi_resolver.py).

        O conteúdo da IEC combina título + resumo (quando há resumo)
        para que a inferência semântica (inference/inference.py, que
        compara embeddings) tenha texto suficiente para comparar --
        um título sozinho costuma ser curto demais para produzir
        conexões semânticas úteis.
        """
        self._require_fields(record, ("title",), origin="acquisition_record")

        iec_id = self._derive_id(record)
        content = self._derive_content(record)

        metadata = {
            "title": record.get("title"),
            "origin": "acquisition_pipeline",
            "source": record.get("source"),
            "merged_sources": record.get("merged_sources"),
            "external_id": record.get("external_id"),
            "doi": record.get("doi"),
            "authors": record.get("authors"),
            "journal": record.get("journal"),
            "publication_date": record.get("publication_date"),
            "url": record.get("url"),
            "retrieved_at": record.get("retrieved_at"),
            "raw": record.get("raw"),
            "raw_by_source": record.get("raw_by_source"),
        }

        iec = self.engine.create_iec(
            id=iec_id,
            content=content,
            node_type=node_type,
            metadata=metadata,
        )
        self.built_count += 1
        return iec

    # ==========================================================
    # 3. EM LOTE -- resiliente, mesmo padrão de tolerância a falha
    #    parcial já usado em AcquisitionPipeline.search_all()
    # ==========================================================

    def build_many_from_acquisition(
        self,
        records: List[Dict[str, Any]],
        node_type: str = "Literatura Científica",
        graph: Optional[Any] = None,
        skip_existing: bool = True,
    ) -> List[Any]:
        """
        Constrói uma IEC para cada registro de `records` (tipicamente
        o `records` devolvido por AcquisitionPipeline.run()).

        Um registro malformado (sem título) não derruba o lote --
        é registrado em `self.skipped` com o motivo, e os demais
        continuam sendo construídos (mesmo princípio de
        AcquisitionPipeline: uma falha isolada não compromete o
        resto). Quando `graph` é passado e `skip_existing` (padrão),
        registros cujo id derivado já existe no grafo são pulados
        também -- evita reconstruir a mesma IEC a cada nova busca
        pela mesma literatura.
        """
        built = []

        for record in records:
            identifier = record.get("doi") or record.get("external_id") or record.get("title")

            iec_id = self._derive_id(record)
            if skip_existing and graph is not None and graph.get_node(iec_id) is not None:
                self.skipped.append({"record": identifier, "reason": "already_in_graph"})
                continue

            try:
                iec = self.build_from_acquisition_record(record, node_type=node_type)
            except ValueError as exc:
                self.skipped.append({"record": identifier, "reason": str(exc)})
                continue

            built.append(iec)

        return built

    # ==========================================================
    # HELPERS INTERNOS
    # ==========================================================

    def _require_fields(self, record: Dict[str, Any], fields: tuple, origin: str) -> None:
        """
        Integridade estrutural, não julgamento de mérito -- mesmo
        princípio de ManualAcquisition._validate_integrity: só
        confere que os campos obrigatórios estão presentes e não
        vazios.
        """
        for field in fields:
            value = record.get(field)
            if not value or not str(value).strip():
                raise ValueError(
                    f"Registro de {origin} sem o campo obrigatório '{field}' preenchido"
                )

    def _derive_id(self, record: Dict[str, Any]) -> str:
        """
        Deriva um id determinístico para a IEC, na ordem de
        confiabilidade da identidade da fonte: DOI (o mais estável
        entre fontes) > id nativo da fonte > hash do título (último
        recurso, quando nem DOI nem external_id existem).
        """
        doi = record.get("doi")
        if doi:
            return f"IEC-DOI-{doi}"

        source = record.get("source")
        external_id = record.get("external_id")
        if source and external_id:
            return f"IEC-{source}-{external_id}"

        title_hash = hashlib.sha1(record.get("title", "").strip().lower().encode("utf-8")).hexdigest()[:12]
        return f"IEC-TITLE-{title_hash}"

    def _derive_content(self, record: Dict[str, Any]) -> str:
        title = (record.get("title") or "").strip()
        abstract = (record.get("abstract") or "").strip()
        if abstract:
            return f"{title}\n\n{abstract}"
        return title

    # ==========================================================
    # CONSULTAS / OBSERVABILIDADE
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Métricas de uso deste builder."""
        return {
            "built": self.built_count,
            "skipped": len(self.skipped),
            "last_skipped": self.skipped[-5:],
        }

    def __repr__(self) -> str:
        return f"IECBuilder(built={self.built_count}, skipped={len(self.skipped)})"
