from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class KnowledgeNode:
    """Unidade estrutural persistente do Knowledge Graph.

    IEC é uma entidade epistemológica e pode ser representada por um
    KnowledgeNode, mas não é o próprio KnowledgeNode.
    """

    node_id: str
    node_type: str
    label: str
    description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def id(self) -> str:
        return self.node_id

    def update(self, **properties: Any) -> None:
        self.properties.update(properties)
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "description": self.description,
            "properties": dict(self.properties),
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
