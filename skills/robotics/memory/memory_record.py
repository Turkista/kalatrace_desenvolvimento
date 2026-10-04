"""
KALATRACE Robotics Memory Record

Represents a single memory generated
during the robot lifecycle.

A MemoryRecord stores an event,
observation or state that may later
be recalled by higher cognitive layers.
"""

from datetime import datetime, UTC
from copy import deepcopy


class MemoryRecord:
    """
    Represents one robotic memory.
    """

    def __init__(
        self,
        memory_id: str,
        source: str,
        memory_type: str,
        content: dict,
        confidence: float = None,
        metadata: dict = None
    ):

        self.memory_id = memory_id

        self.source = source

        self.memory_type = memory_type

        self.content = deepcopy(content)

        self.confidence = confidence

        self.metadata = deepcopy(
            metadata or {}
        )

        self.created_at = datetime.now(UTC)

    def to_dict(self):
        """
        Convert memory into a
        serializable structure.
        """

        return {

            "memory_id":
                self.memory_id,

            "source":
                self.source,

            "memory_type":
                self.memory_type,

            "content":
                deepcopy(self.content),

            "confidence":
                self.confidence,

            "metadata":
                deepcopy(self.metadata),

            "created_at":
                self.created_at
        }