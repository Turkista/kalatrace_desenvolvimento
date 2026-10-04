"""
Tests for KALATRACE Robotics Memory Store
"""

from skills.robotics.memory.memory_record import (
    MemoryRecord
)

from skills.robotics.memory.memory_store import (
    MemoryStore
)


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


def test_add_memory():

    store = MemoryStore()

    memory = create_memory()


    store.add_memory(
        memory
    )


    assert (
        store.memory_count()
        == 1
    )

    assert (
        store.contains(
            "MEM-001"
        )
    )


def test_get_memory():

    store = MemoryStore()

    memory = create_memory()


    store.add_memory(
        memory
    )


    recovered = store.get_memory(
        "MEM-001"
    )


    assert (
        recovered.memory_id
        == "MEM-001"
    )


def test_remove_memory():

    store = MemoryStore()

    memory = create_memory()


    store.add_memory(
        memory
    )

    store.remove_memory(
        "MEM-001"
    )


    assert (
        store.memory_count()
        == 0
    )

    assert (
        not store.contains(
            "MEM-001"
        )
    )


def test_list_memories():

    store = MemoryStore()


    store.add_memory(
        create_memory("MEM-001")
    )

    store.add_memory(
        create_memory("MEM-002")
    )


    memories = store.list_memories()


    assert (
        len(memories)
        == 2
    )

    assert (
        "MEM-001"
        in memories
    )

    assert (
        "MEM-002"
        in memories
    )


def test_export():

    store = MemoryStore()


    store.add_memory(
        create_memory()
    )


    exported = store.export()


    assert (
        "MEM-001"
        in exported
    )

    assert (
        exported["MEM-001"]["source"]
        == "perception"
    )


def test_clear():

    store = MemoryStore()


    store.add_memory(
        create_memory("MEM-001")
    )

    store.add_memory(
        create_memory("MEM-002")
    )


    store.clear()


    assert (
        store.memory_count()
        == 0
    )

    assert (
        store.list_memories()
        == {}
    )