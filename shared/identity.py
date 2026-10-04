"""
KALATRACE
Identity System

Camada:
Foundation Layer

Responsabilidade:
Criar, representar e controlar identificadores
universais das entidades do sistema.

Blueprint:
Documento 71
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from shared.enums import IdentifierType


# ==========================================================
# Identity Base
# ==========================================================


@dataclass(frozen=True)
class Identity:
    """
    Identidade universal de uma entidade KALATRACE.

    Toda entidade persistente deve possuir uma Identity.
    """

    id: UUID = field(default_factory=uuid4)

    identifier_type: IdentifierType = IdentifierType.KNOWLEDGE

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    def __str__(self) -> str:
        """
        Representação textual simples.
        """

        return f"{self.identifier_type.value}:{self.id}"


    def to_dict(self) -> dict:
        """
        Conversão para persistência/API.
        """

        return {
            "id": str(self.id),
            "type": self.identifier_type.value,
            "created_at": self.created_at.isoformat()
        }
# ==========================================================
# Identifier Generator
# ==========================================================


class IdentifierGenerator:
    """
    Gerador central de identificadores KALATRACE.

    Responsável por criar identidades padronizadas
    para entidades do sistema.
    """


    PREFIX_MAP = {

        IdentifierType.IEC:
            "IEC",

        IdentifierType.EVIDENCE:
            "EVD",

        IdentifierType.HYPOTHESIS:
            "HYP",

        IdentifierType.CONCEPT:
            "CON",

        IdentifierType.QUESTION:
            "QST",

        IdentifierType.DISCOVERY:
            "DSC",

        IdentifierType.INSIGHT:
            "INS",

        IdentifierType.AGENT:
            "AGT",

        IdentifierType.ENGINE:
            "ENG",

        IdentifierType.EVENT:
            "EVT",
    }


    @classmethod
    def generate(
        cls,
        identifier_type: IdentifierType
    ) -> str:
        """
        Gera um identificador legível.

        Exemplo:

        IEC-000001-A7F42C
        """

        prefix = cls.PREFIX_MAP.get(
            identifier_type,
            "UNK"
        )


        unique = uuid4().hex[:6].upper()


        return (
            f"{prefix}-"
            f"{unique}"
        )
# ==========================================================
# Entity Identity
# ==========================================================


@dataclass(frozen=True)
class EntityIdentity:
    """
    Identidade completa de uma entidade KALATRACE.

    Diferente de Identity, esta classe contém
    informações adicionais necessárias para
    rastreabilidade epistemológica.
    """


    identifier: str

    identifier_type: IdentifierType


    uuid: UUID = field(
        default_factory=uuid4
    )


    namespace: str = "KALATRACE"


    created_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )


    metadata: dict = field(
        default_factory=dict
    )


    def describe(self) -> dict:
        """
        Retorna uma descrição completa
        da identidade.
        """

        return {

            "namespace":
                self.namespace,

            "identifier":
                self.identifier,

            "uuid":
                str(self.uuid),

            "type":
                self.identifier_type.value,

            "created_at":
                self.created_at.isoformat(),

            "metadata":
                self.metadata
        }



    def belongs_to(
        self,
        namespace: str
    ) -> bool:
        """
        Verifica se a identidade pertence
        a determinado namespace.
        """

        return (
            self.namespace == namespace
        )
# ==========================================================
# Identity Factory
# ==========================================================


class IdentityFactory:
    """
    Fábrica central de identidades KALATRACE.

    Responsável por criar identidades padronizadas
    para qualquer entidade do sistema.
    """


    @staticmethod
    def create(
        identifier_type: IdentifierType,
        metadata: dict | None = None
    ) -> EntityIdentity:
        """
        Cria uma nova identidade.

        Exemplo:

        IdentityFactory.create(
            IdentifierType.IEC
        )

        Retorno:

        IEC-A92F31
        """


        identifier = IdentifierGenerator.generate(
            identifier_type
        )


        return EntityIdentity(

            identifier=identifier,

            identifier_type=identifier_type,

            metadata=metadata or {}

        )



    @staticmethod
    def recreate(
        identifier: str,
        identifier_type: IdentifierType,
        uuid: UUID,
        metadata: dict | None = None,
        created_at: datetime | None = None
    ) -> EntityIdentity:
        """
        Reconstrói uma identidade existente.

        Usado na recuperação de dados
        persistidos.
        """


        return EntityIdentity(

            identifier=identifier,

            identifier_type=identifier_type,

            uuid=uuid,

            metadata=metadata or {},

            created_at=
            created_at
            or datetime.now(timezone.utc)

        )
# ==========================================================
# Identity Validation
# ==========================================================


def validate_identifier(
    identifier: str
) -> bool:
    """
    Valida se um identificador
    segue o padrão KALATRACE.

    Exemplos válidos:

    IEC-A82F91
    EVD-91AB42
    HYP-7FA912
    """


    if not identifier:
        return False


    parts = identifier.split("-")


    if len(parts) != 2:
        return False


    prefix, value = parts


    if len(prefix) != 3:
        return False


    if len(value) != 6:
        return False


    return True



# ==========================================================
# Identity Utilities
# ==========================================================


def extract_identifier_type(
    identifier: str
) -> IdentifierType | None:
    """
    Recupera o tipo de entidade
    através do prefixo.
    """


    prefix_map = {

        "IEC":
            IdentifierType.IEC,

        "EVD":
            IdentifierType.EVIDENCE,

        "HYP":
            IdentifierType.HYPOTHESIS,

        "CON":
            IdentifierType.CONCEPT,

        "QST":
            IdentifierType.QUESTION,

        "DSC":
            IdentifierType.DISCOVERY,

        "INS":
            IdentifierType.INSIGHT,

        "AGT":
            IdentifierType.AGENT,

        "ENG":
            IdentifierType.ENGINE,

        "EVT":
            IdentifierType.EVENT,
    }


    prefix = identifier.split("-")[0]


    return prefix_map.get(prefix)



def create_system_identity() -> EntityIdentity:
    """
    Cria a identidade principal do sistema.
    """

    return EntityIdentity(

        identifier="KALATRACE",

        identifier_type=IdentifierType.ENGINE,

        namespace="KALATRACE",

        metadata={
            "system": "KALATRACE",
            "layer": "foundation"
        }
    )