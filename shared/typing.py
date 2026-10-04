"""
KALATRACE
Typing System

Foundation Layer

Responsabilidade:
Definir tipos compartilhados
por toda arquitetura.

Blueprint:
Documento 71
"""


from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    TypeAlias
)



# ==========================================================
# Primitive Types
# ==========================================================


StringID: TypeAlias = str


EntityID: TypeAlias = str


Identifier: TypeAlias = str


VersionString: TypeAlias = str


TimestampString: TypeAlias = str



JSONPrimitive: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None
]



JSONData: TypeAlias = Dict[
    str,
    Any
]
# ==========================================================
# Scientific Entity Types
# ==========================================================


Metadata: TypeAlias = Dict[
    str,
    Any
]


Attributes: TypeAlias = Dict[
    str,
    Any
]


Configuration: TypeAlias = Dict[
    str,
    Any
]


Parameters: TypeAlias = Dict[
    str,
    Any
]



# ==========================================================
# Knowledge Structures
# ==========================================================


EvidenceData: TypeAlias = Dict[
    str,
    Any
]


HypothesisData: TypeAlias = Dict[
    str,
    Any
]


RelationshipData: TypeAlias = Dict[
    str,
    Any
]


GraphNodeData: TypeAlias = Dict[
    str,
    Any
]


GraphEdgeData: TypeAlias = Dict[
    str,
    Any
]



# ==========================================================
# Collections
# ==========================================================


EntityList: TypeAlias = List[
    EntityID
]


IdentifierList: TypeAlias = List[
    Identifier
]


MetadataList: TypeAlias = List[
    Metadata
]
# ==========================================================
# Engine Communication Types
# ==========================================================


ResultData: TypeAlias = Dict[
    str,
    Any
]


ResponseData: TypeAlias = Dict[
    str,
    Any
]


RequestData: TypeAlias = Dict[
    str,
    Any
]



# ==========================================================
# Processing Results
# ==========================================================


Score: TypeAlias = float


ConfidenceValue: TypeAlias = float


Probability: TypeAlias = float


PriorityValue: TypeAlias = float



# ==========================================================
# Engine States
# ==========================================================


StateName: TypeAlias = str


EventName: TypeAlias = str


ActionName: TypeAlias = str



# ==========================================================
# Generic Identifiers
# ==========================================================


AgentID: TypeAlias = str


EngineID: TypeAlias = str


RegistryID: TypeAlias = str


RepositoryID: TypeAlias = str


SessionID: TypeAlias = str


TransactionID: TypeAlias = str
# ==========================================================
# Utility Types
# ==========================================================


PathString: TypeAlias = str


FileName: TypeAlias = str


URLString: TypeAlias = str


HashValue: TypeAlias = str



# ==========================================================
# Optional Types
# ==========================================================


OptionalMetadata: TypeAlias = Optional[
    Metadata
]


OptionalEntityID: TypeAlias = Optional[
    EntityID
]



# ==========================================================
# Module Exports
# ==========================================================


__all__ = [

    "StringID",
    "EntityID",
    "Identifier",
    "VersionString",
    "TimestampString",

    "JSONPrimitive",
    "JSONData",

    "Metadata",
    "Attributes",
    "Configuration",
    "Parameters",

    "EvidenceData",
    "HypothesisData",
    "RelationshipData",
    "GraphNodeData",
    "GraphEdgeData",

    "EntityList",
    "IdentifierList",
    "MetadataList",

    "ResultData",
    "ResponseData",
    "RequestData",

    "Score",
    "ConfidenceValue",
    "Probability",
    "PriorityValue",

    "StateName",
    "EventName",
    "ActionName",

    "AgentID",
    "EngineID",
    "RegistryID",
    "RepositoryID",
    "SessionID",
    "TransactionID",

    "PathString",
    "FileName",
    "URLString",
    "HashValue",

    "OptionalMetadata",
    "OptionalEntityID"

]