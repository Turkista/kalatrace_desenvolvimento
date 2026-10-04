"""
KALATRACE Robotics Memory Pipeline

Coordinates the complete robotic memory flow.

The pipeline orchestrates the following
components:

- MemoryManager
- MemoryStore

The pipeline does not store memories
directly. It coordinates the memory cycle.
"""

from copy import deepcopy


class MemoryPipeline:
    """
    Coordinates robotic memory.
    """

    def __init__(
        self,
        memory_manager
    ):

        self.memory_manager = memory_manager

    def process(
        self,
        memory
    ):
        """
        Store one memory and return the
        current memory snapshot.
        """

        self.memory_manager.remember(
            memory
        )

        return self.export()

    def recall(
        self,
        memory_id: str
    ):
        """
        Retrieve one memory.
        """

        return self.memory_manager.recall(
            memory_id
        )

    def recall_all(self):
        """
        Return every stored memory.
        """

        return deepcopy(
            self.memory_manager.recall_all()
        )

    def memory_count(self):
        """
        Return the number of memories.
        """

        return self.memory_manager.memory_count()

    def clear(self):
        """
        Clear every stored memory.
        """

        self.memory_manager.clear()

    def export(self):
        """
        Export current memory state.
        """

        return {

            "memory_count":
                self.memory_manager.memory_count(),

            "memories":
                self.memory_manager.export()
        }