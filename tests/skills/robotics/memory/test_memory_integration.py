"""
KALATRACE Robotics Memory Integration Tests
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


def create_memory_system():

    store = MemoryStore()

    manager = MemoryManager(store)

    pipeline = MemoryPipeline(manager)

    return (

        store,

        manager,

        pipeline
    )


def create_memory(
    memory_id,
    obj
):

    return MemoryRecord(

        memory_id=memory_id,

        source="perception",

        memory_type="object_detection",

        content={

            "object": obj
        },

        confidence=0.95
    )


def test_complete_memory_cycle():

    (

        store,

        manager,

        pipeline

    ) = create_memory_system()


    pipeline.process(

        create_memory(

            "MEM-001",

            "person"
        )
    )


    pipeline.process(

        create_memory(

            "MEM-002",

            "chair"
        )
    )


    snapshot = pipeline.export()


    assert snapshot["memory_count"] == 2

    assert "MEM-001" in snapshot["memories"]

    assert "MEM-002" in snapshot["memories"]

    assert (

        snapshot["memories"]["MEM-001"]["content"]["object"]

        == "person"

    )


def test_memory_recall():

    (

        store,

        manager,

        pipeline

    ) = create_memory_system()


    pipeline.process(

        create_memory(

            "MEM-100",

            "door"
        )
    )


    memory = pipeline.recall(

        "MEM-100"
    )


    assert (

        memory.memory_id

        == "MEM-100"

    )

    assert (

        memory.content["object"]

        == "door"

    )


def test_memory_clear():

    (

        store,

        manager,

        pipeline

    ) = create_memory_system()


    pipeline.process(

        create_memory(

            "MEM-001",

            "person"
        )
    )


    pipeline.process(

        create_memory(

            "MEM-002",

            "vehicle"
        )
    )


    pipeline.clear()


    exported = pipeline.export()


    assert exported["memory_count"] == 0

    assert exported["memories"] == {}