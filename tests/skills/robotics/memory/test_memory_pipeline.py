"""
Tests for KALATRACE Robotics Memory Pipeline
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

from skills.robotics.memory.memory_pipeline import (
    MemoryPipeline
)


def create_pipeline():

    store = MemoryStore()

    manager = MemoryManager(store)

    pipeline = MemoryPipeline(manager)

    return pipeline


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


def test_process():

    pipeline = create_pipeline()

    memory = create_memory()

    snapshot = pipeline.process(memory)

    assert snapshot["memory_count"] == 1

    assert "MEM-001" in snapshot["memories"]


def test_recall():

    pipeline = create_pipeline()

    memory = create_memory()

    pipeline.process(memory)

    recalled = pipeline.recall("MEM-001")

    assert recalled.memory_id == "MEM-001"


def test_recall_all():

    pipeline = create_pipeline()

    pipeline.process(
        create_memory("MEM-001")
    )

    pipeline.process(
        create_memory("MEM-002")
    )

    memories = pipeline.recall_all()

    assert len(memories) == 2

    assert "MEM-001" in memories

    assert "MEM-002" in memories


def test_export():

    pipeline = create_pipeline()

    pipeline.process(
        create_memory()
    )

    exported = pipeline.export()

    assert exported["memory_count"] == 1

    assert "MEM-001" in exported["memories"]


def test_clear():

    pipeline = create_pipeline()

    pipeline.process(
        create_memory("MEM-001")
    )

    pipeline.process(
        create_memory("MEM-002")
    )

    pipeline.clear()

    exported = pipeline.export()

    assert exported["memory_count"] == 0

    assert exported["memories"] == {}