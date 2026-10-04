"""
KALATRACE Robotics Memory Store

Stores and manages robotic memories.

The Memory Store acts as the robot's
short-term memory repository.
"""

from copy import deepcopy


class MemoryStore:
    """
    Stores robotic memories.
    """

    def __init__(self):

        self.memories = {}

    def add_memory(
        self,
        memory
    ):
        """
        Store a memory.
        """

        self.memories[
            memory.memory_id
        ] = memory

    def remove_memory(
        self,
        memory_id: str
    ):
        """
        Remove a memory.
        """

        self.memories.pop(
            memory_id,
            None
        )

    def get_memory(
        self,
        memory_id: str
    ):
        """
        Return one memory.
        """

        return self.memories.get(
            memory_id
        )

    def contains(
        self,
        memory_id: str
    ):
        """
        Check if a memory exists.
        """

        return (
            memory_id
            in self.memories
        )

    def memory_count(self):
        """
        Return the number of memories.
        """

        return len(
            self.memories
        )

    def list_memories(self):
        """
        Return all memories.
        """

        return deepcopy(
            self.memories
        )

    def clear(self):
        """
        Remove every memory.
        """

        self.memories.clear()

    def export(self):
        """
        Export every stored memory.
        """

        exported = {}

        for memory_id, memory in self.memories.items():

            exported[memory_id] = (
                memory.to_dict()
            )

        return exported