"""
KALATRACE Robotics Memory Manager

Coordinates the robot memory lifecycle.

The Memory Manager provides a high-level
interface for storing, retrieving and
managing robotic memories.
"""

from copy import deepcopy


class MemoryManager:
    """
    Coordinates robotic memory.
    """

    def __init__(
        self,
        memory_store
    ):

        self.memory_store = memory_store

    def remember(
        self,
        memory
    ):
        """
        Store a memory.
        """

        self.memory_store.add_memory(
            memory
        )

    def forget(
        self,
        memory_id: str
    ):
        """
        Remove a memory.
        """

        self.memory_store.remove_memory(
            memory_id
        )

    def recall(
        self,
        memory_id: str
    ):
        """
        Retrieve one memory.
        """

        return self.memory_store.get_memory(
            memory_id
        )

    def contains(
        self,
        memory_id: str
    ):
        """
        Check whether a memory exists.
        """

        return self.memory_store.contains(
            memory_id
        )

    def recall_all(self):
        """
        Return every stored memory.
        """

        return deepcopy(
            self.memory_store.list_memories()
        )

    def memory_count(self):
        """
        Return the number of memories.
        """

        return self.memory_store.memory_count()

    def clear(self):
        """
        Remove every stored memory.
        """

        self.memory_store.clear()

    def export(self):
        """
        Export memory store.
        """

        return self.memory_store.export()