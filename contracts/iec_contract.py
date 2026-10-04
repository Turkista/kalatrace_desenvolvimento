from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime, UTC


@dataclass
class IECContract:
    """
    Contrato base da Informational Epistemic Cell.

    Representa uma unidade de conhecimento
    dentro do KALATRACE.
    """

    iec_id: str

    title: str

    statement: str

    knowledge_type: str

    confidence: float = 0.0

    status: str = "active"

    evidence_ids: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: str = field(
        default_factory=lambda:
        datetime.now(UTC).isoformat()
    )

    updated_at: str = field(
        default_factory=lambda:
        datetime.now(UTC).isoformat()
    )
    # ==========================================================
    # VALIDAÇÃO E CONTROLE EPISTEMOLÓGICO
    # ==========================================================

    def validate(self) -> bool:
        """
        Verifica se a IEC possui os campos
        mínimos necessários para existir no sistema.
        """

        required_fields = [
            "iec_id",
            "title",
            "statement",
            "knowledge_type"
        ]

        for field_name in required_fields:

            value = getattr(
                self,
                field_name,
                None
            )

            if not value:
                raise ValueError(
                    f"Campo obrigatório ausente: {field_name}"
                )


        if not isinstance(
            self.confidence,
            (int, float)
        ):
            raise TypeError(
                "confidence deve ser numérico"
            )


        if self.confidence < 0 or self.confidence > 1:
            raise ValueError(
                "confidence deve estar entre 0 e 1"
            )


        return True



    def add_evidence(
        self,
        evidence_id: str
    ):
        """
        Cria vínculo entre a IEC
        e uma evidência científica.
        """

        if evidence_id not in self.evidence_ids:

            self.evidence_ids.append(
                evidence_id
            )


            self._register_history(
                "evidence_added",
                {
                    "evidence_id": evidence_id
                }
            )



    def remove_evidence(
        self,
        evidence_id: str
    ):
        """
        Remove vínculo com uma evidência.
        """

        if evidence_id in self.evidence_ids:

            self.evidence_ids.remove(
                evidence_id
            )


            self._register_history(
                "evidence_removed",
                {
                    "evidence_id": evidence_id
                }
            )



    def update_confidence(
        self,
        new_confidence: float,
        reason: str
    ):
        """
        Atualiza o nível de confiança
        epistemológica da IEC.
        """

        if new_confidence < 0 or new_confidence > 1:
            raise ValueError(
                "confidence deve estar entre 0 e 1"
            )


        previous = self.confidence


        self.confidence = float(
            new_confidence
        )


        self.updated_at = (
            datetime.now(UTC)
            .isoformat()
        )


        self._register_history(
            "confidence_update",
            {
                "previous": previous,
                "new": new_confidence,
                "reason": reason
            }
        )
    # ==========================================================
    # HISTÓRICO, SERIALIZAÇÃO E REPRESENTAÇÃO
    # ==========================================================

    def _register_history(
        self,
        event: str,
        details: Dict[str, Any]
    ):
        """
        Registra eventos importantes
        da evolução da IEC.
        """

        if "history" not in self.metadata:

            self.metadata["history"] = []


        self.metadata["history"].append(
            {
                "event": event,
                "details": details,
                "timestamp": datetime.now(UTC)
                .isoformat()
            }
        )



    def change_status(
        self,
        new_status: str,
        reason: str
    ):
        """
        Altera o estado da IEC.
        """

        previous_status = self.status


        self.status = new_status


        self.updated_at = (
            datetime.now(UTC)
            .isoformat()
        )


        self._register_history(
            "status_changed",
            {
                "previous": previous_status,
                "new": new_status,
                "reason": reason
            }
        )



    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a IEC para formato
        persistível.
        """

        return {

            "iec_id": self.iec_id,

            "title": self.title,

            "statement": self.statement,

            "knowledge_type": self.knowledge_type,

            "confidence": self.confidence,

            "status": self.status,

            "evidence_ids": self.evidence_ids,

            "metadata": self.metadata,

            "created_at": self.created_at,

            "updated_at": self.updated_at
        }



    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ):
        """
        Reconstrói uma IEC
        a partir de um dicionário.
        """

        return cls(

            iec_id=data.get(
                "iec_id"
            ),

            title=data.get(
                "title"
            ),

            statement=data.get(
                "statement"
            ),

            knowledge_type=data.get(
                "knowledge_type"
            ),

            confidence=data.get(
                "confidence",
                0.0
            ),

            status=data.get(
                "status",
                "active"
            ),

            evidence_ids=data.get(
                "evidence_ids",
                []
            ),

            metadata=data.get(
                "metadata",
                {}
            ),

            created_at=data.get(
                "created_at"
            ),

            updated_at=data.get(
                "updated_at"
            )
        )



    def __repr__(self) -> str:
        """
        Representação resumida da IEC.
        """

        return (

            f"IECContract("
            f"id={self.iec_id}, "
            f"type={self.knowledge_type}, "
            f"confidence={self.confidence}"
            f")"

        )