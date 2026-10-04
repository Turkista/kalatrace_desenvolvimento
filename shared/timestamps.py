"""
KALATRACE
Timestamp Management System

Foundation Layer

Responsabilidade:
Controle temporal das entidades,
eventos e evolução do conhecimento.

Blueprint:
Documento 71
"""


from dataclasses import dataclass, field
from datetime import datetime, timezone



# ==========================================================
# Timestamp Core
# ==========================================================


@dataclass(frozen=True)
class Timestamp:
    """
    Representa uma marca temporal KALATRACE.

    Usado para registrar:

    - criação
    - atualização
    - validação
    - observação
    - eventos
    """


    value: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )



    def isoformat(self) -> str:
        """
        Retorna formato ISO para
        armazenamento e APIs.
        """

        return self.value.isoformat()



    def to_dict(self) -> dict:
        """
        Serialização.
        """

        return {

            "timestamp":
                self.isoformat()

        }



    def __str__(self):

        return self.isoformat()
# ==========================================================
# Temporal Event Types
# ==========================================================


from enum import StrEnum



class TemporalEventType(StrEnum):
    """
    Tipos de eventos temporais
    reconhecidos pelo KALATRACE.
    """


    CREATED = "created"

    UPDATED = "updated"

    VERIFIED = "verified"

    VALIDATED = "validated"

    OBSERVED = "observed"

    DISCOVERED = "discovered"

    ARCHIVED = "archived"



# ==========================================================
# Temporal Event
# ==========================================================


@dataclass(frozen=True)
class TemporalEvent:
    """
    Evento temporal associado
    a uma entidade.
    """


    event_type: TemporalEventType


    timestamp: Timestamp = field(
        default_factory=Timestamp
    )


    description: str = ""



    source: str = "KALATRACE"



    def to_dict(self) -> dict:
        """
        Conversão para persistência.
        """

        return {

            "event_type":
                self.event_type.value,


            "timestamp":
                self.timestamp.isoformat(),


            "description":
                self.description,


            "source":
                self.source

        }
# ==========================================================
# Lifecycle Clock
# ==========================================================


@dataclass
class LifecycleClock:
    """
    Controlador temporal do ciclo de vida
    de uma entidade KALATRACE.

    Mantém os principais momentos
    de existência de um objeto.
    """


    created_at: Timestamp = field(
        default_factory=Timestamp
    )


    updated_at: Timestamp | None = None


    verified_at: Timestamp | None = None


    archived_at: Timestamp | None = None



    def update(self):
        """
        Registra atualização da entidade.
        """

        self.updated_at = Timestamp()



    def verify(self):
        """
        Registra validação/verificação.
        """

        self.verified_at = Timestamp()



    def archive(self):
        """
        Registra arquivamento.
        """

        self.archived_at = Timestamp()



    def age_seconds(self) -> float:
        """
        Calcula idade da entidade
        em segundos.
        """

        now = datetime.now(
            timezone.utc
        )


        return (
            now -
            self.created_at.value
        ).total_seconds()



    def to_dict(self) -> dict:
        """
        Serialização completa
        do ciclo de vida.
        """

        return {

            "created_at":
                self.created_at.isoformat(),


            "updated_at":
                (
                    self.updated_at.isoformat()
                    if self.updated_at
                    else None
                ),


            "verified_at":
                (
                    self.verified_at.isoformat()
                    if self.verified_at
                    else None
                ),


            "archived_at":
                (
                    self.archived_at.isoformat()
                    if self.archived_at
                    else None
                )

        }
# ==========================================================
# Timestamp Manager
# ==========================================================


class TimestampManager:
    """
    Gerenciador central de timestamps.

    Evita que cada módulo crie
    datas de forma independente.

    Mantém padronização temporal
    no ecossistema KALATRACE.
    """



    @staticmethod
    def now() -> Timestamp:
        """
        Retorna o momento atual
        no padrão KALATRACE.
        """

        return Timestamp()



    @staticmethod
    def create_event(
        event_type: TemporalEventType,
        description: str = "",
        source: str = "KALATRACE"
    ) -> TemporalEvent:
        """
        Cria um evento temporal.
        """

        return TemporalEvent(

            event_type=event_type,

            timestamp=TimestampManager.now(),

            description=description,

            source=source

        )



    @staticmethod
    def lifecycle_start() -> LifecycleClock:
        """
        Inicializa um ciclo de vida.
        """

        return LifecycleClock()
# ==========================================================
# Timestamp Validation
# ==========================================================


def validate_timestamp(
    timestamp: Timestamp
) -> bool:
    """
    Valida se um timestamp
    possui uma data válida.
    """


    if not isinstance(
        timestamp,
        Timestamp
    ):
        return False


    return isinstance(
        timestamp.value,
        datetime
    )



def compare_timestamps(
    first: Timestamp,
    second: Timestamp
) -> int:
    """
    Compara dois timestamps.

    Retornos:

    -1 primeiro é anterior
     0 iguais
     1 primeiro é posterior
    """


    if first.value < second.value:
        return -1


    if first.value > second.value:
        return 1


    return 0



# ==========================================================
# Module Exports
# ==========================================================


__all__ = [

    "Timestamp",

    "TemporalEventType",

    "TemporalEvent",

    "LifecycleClock",

    "TimestampManager",

    "validate_timestamp",

    "compare_timestamps"

]