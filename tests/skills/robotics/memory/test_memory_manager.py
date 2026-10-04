"""
Tests for KALATRACE Robotics Memory Manager
"""

from skills.robotics.memory.memory_record import (
    MemoryRecord
)

from skills.robotics.memory.memory_store import (
    MemoryStore
)

from skills.robotics.memory.memory_manager import (
    MemoryManager
)


def create_manager():

    store = MemoryStore()

    manager = MemoryManager(store)

    return manager


def create_memory(
    memory_id="MEM-001"
):

    return MemoryRecord(

        memory_id=memory_id,

        source="perception",

        memory_type="object_detection",

        content={
            "object": "person"
        }
    )


def test_remember():

    manager = create_manager()

    memory = create_memory()

    manager.remember(memory)

    assert manager.memory_count() == 1

    assert manager.contains("MEM-001")


def test_recall():

    manager = create_manager()

    memory = create_memory()

    manager.remember(memory)

    recalled = manager.recall("MEM-001")

    assert recalled.memory_id == "MEM-001"


def test_recall_all():

    manager = create_manager()

    manager.remember(
        create_memory("MEM-001")
    )

    manager.remember(
        create_memory("MEM-002")
    )

    memories = manager.recall_all()

    assert len(memories) == 2

    assert "MEM-001" in memories

    assert "MEM-002" in memories


def test_forget():

    manager = create_manager()

    manager.remember(
        create_memory()
    )

    manager.forget("MEM-001")

    assert manager.memory_count() == 0

    assert not manager.contains("MEM-001")


def test_export():

    manager = create_manager()

    manager.remember(
        create_memory()
    )

    exported = manager.export()

    assert "MEM-001" in exported

    assert (
        exported["MEM-001"]["source"]
        == "perception"
    )


def test_clear():

    manager = create_manager()

    manager.remember(
        create_memory("MEM-001")
    )

    manager.remember(
        create_memory("MEM-002")
    )

    manager.clear()

    assert manager.memory_count() == 0