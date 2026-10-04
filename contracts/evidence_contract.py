from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Dict, Any, Optional


@dataclass
class EvidenceContract:
    """
    Contrato estrutural de uma Evidência.

    Define o formato padronizado utilizado
    entre os módulos do KALATRACE.
    """

    # ==========================================
    # IDENTIDADE
    # ==========================================

    id: str

    title: str

    # ==========================================
    # DESCRIÇÃO
    # ==========================================

    description: str

    evidence_type: str

    # ==========================================
    # ORIGEM
    # ==========================================

    source: Optional[str] = None

    doi: Optional[str] = None

    pmid: Optional[str] = None

    url: Optional[str] = None

    # ==========================================
    # CLASSIFICAÇÃO
    # ==========================================

    domain: Optional[str] = None

    category: Optional[str] = None

    # ==========================================
    # AVALIAÇÃO
    # ==========================================

    confidence: float = 0.50

    evidence_level: Optional[str] = None

    quality_score: float = 0.50

    # ==========================================
    # CICLO DE VIDA
    # ==========================================

    version: int = 1

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    # ==========================================
    # METADADOS
    # ==========================================

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ==========================================
    # COMPATIBILIDADE
    # ==========================================
    # storage/evidence_store.py e validation/evidence_validation_engine.py
    # (antes core/validation_engine.py, movido em T1.4b) consomem
    # `evidence.evidence_id`; o campo do dataclass
    # é `id`. Alias mantido para não exigir mudança nos
    # call-sites existentes (achado T0.5).

    @property
    def evidence_id(self) -> str:
        return self.id

    # ==========================================
    # VALIDAÇÃO
    # ==========================================

    def validate(self):
        """
        Valida a integridade estrutural da evidência.

        Esta validação garante apenas que o objeto
        está consistente. A qualidade científica
        será avaliada por módulos especializados.
        """

        if not self.id:
            raise ValueError(
                "Evidence deve possuir um ID."
            )

        if not self.title:
            raise ValueError(
                "Evidence deve possuir um título."
            )

        if not self.description:
            raise ValueError(
                "Evidence deve possuir uma descrição."
            )

        if not self.evidence_type:
            raise ValueError(
                "Evidence deve possuir um tipo."
            )

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Confidence deve estar entre 0 e 1."
            )

        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(
                "Quality Score deve estar entre 0 e 1."
            )

        if self.version < 1:
            raise ValueError(
                "Version deve ser maior ou igual a 1."
            )

        return True
    # ==========================================
    # SERIALIZAÇÃO
    # ==========================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o contrato para um dicionário.

        Utilizado por:
        - APIs
        - Repositórios
        - Persistência
        - Exportação
        """

        return {

            "id": self.id,

            "title": self.title,

            "description": self.description,

            "evidence_type": self.evidence_type,

            "source": self.source,

            "doi": self.doi,

            "pmid": self.pmid,

            "url": self.url,

            "domain": self.domain,

            "category": self.category,

            "confidence": self.confidence,

            "evidence_level": self.evidence_level,

            "quality_score": self.quality_score,

            "version": self.version,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "metadata": dict(self.metadata)

        }


    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> "EvidenceContract":
        """
        Reconstrói um contrato a partir de
        um dicionário.
        """

        return cls(

            id=data["id"],

            title=data["title"],

            description=data["description"],

            evidence_type=data["evidence_type"],

            source=data.get("source"),

            doi=data.get("doi"),

            pmid=data.get("pmid"),

            url=data.get("url"),

            domain=data.get("domain"),

            category=data.get("category"),

            confidence=float(
                data.get(
                    "confidence",
                    0.5
                )
            ),

            evidence_level=data.get(
                "evidence_level"
            ),

            quality_score=float(
                data.get(
                    "quality_score",
                    0.5
                )
            ),

            version=int(
                data.get(
                    "version",
                    1
                )
            ),

            created_at=data.get(
                "created_at",
                datetime.now(UTC)
            ),

            updated_at=data.get(
                "updated_at",
                datetime.now(UTC)
            ),

            metadata=dict(
                data.get(
                    "metadata",
                    {}
                )
            )

        )
    # ==========================================================
    # MÉTODOS DE EVOLUÇÃO DA EVIDÊNCIA
    # ==========================================================
    #
    # NOTA (T0.5, sessão 01/08/2026): este bloco continha uma
    # segunda definição de validate()/to_dict()/from_dict()/__repr__
    # escrita contra um schema de campos que nunca existiu no
    # dataclass (evidence_id, relevance). Como Python usa a última
    # definição de um método dentro da classe, essas versões quebradas
    # sobrescreviam silenciosamente as versões corretas definidas
    # acima, tornando impossível validar ou serializar qualquer
    # EvidenceContract. Bloco duplicado removido; apenas os métodos
    # de evolução de confiança (únicos, não duplicados) permanecem.

    def update_confidence(
        self,
        confidence: float,
        reason: str
    ):
        """
        Atualiza a força epistemológica
        da evidência.
        """

        if confidence < 0 or confidence > 1:
            raise ValueError(
                "confidence deve estar entre 0 e 1"
            )

        previous_confidence = self.confidence

        self.confidence = float(confidence)

        self.metadata.setdefault(
            "confidence_history", []
        ).append(
            {
                "previous": previous_confidence,
                "new": confidence,
                "reason": reason
            }
        )


    def increase_confidence(
        self,
        amount: float,
        reason: str
    ):
        """
        Fortalece a evidência quando novos
        elementos aumentam sua sustentação.
        """

        new_confidence = min(
            self.confidence + amount,
            1.0
        )

        self.update_confidence(
            new_confidence,
            reason
        )


    def decrease_confidence(
        self,
        amount: float,
        reason: str
    ):
        """
        Reduz confiança quando surgem
        inconsistências ou evidências contrárias.
        """

        new_confidence = max(
            self.confidence - amount,
            0.0
        )

        self.update_confidence(
            new_confidence,
            reason
        )
