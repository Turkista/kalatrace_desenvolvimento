"""
Tests for KALATRACE Robotics Memory Record
"""

from datetime import datetime

from skills.robotics.memory.memory_record import (
    MemoryRecord
)


def test_memory_record_creation():

    memory = MemoryRecord(

        memory_id="MEM-001",

        source="perception",

        memory_type="object_detection",

        content={

            "object": "person",

            "position": [10, 5]
        },

        confidence=0.95
    )


    assert (
        memory.memory_id
        == "MEM-001"
    )

    assert (
        memory.source
        == "perception"
    )

    assert (
        memory.memory_type
        == "object_detection"
    )

    assert (
        memory.content["object"]
        == "person"
    )

    assert (
        memory.confidence
        == 0.95
    )

    assert isinstance(
        memory.created_at,
        datetime
    )


def test_memory_record_metadata():

    memory = MemoryRecord(

        memory_id="MEM-002",

        source="navigation",

        memory_type="position",

        content={

            "x": 20,

            "y": 15
        },

        metadata={

            "floor": 2,

            "building": "A"
        }
    )


    assert (
        memory.metadata["floor"]
        == 2
    )

    assert (
        memory.metadata["building"]
        == "A"
    )


def test_memory_record_to_dict():

    memory = MemoryRecord(

        memory_id="MEM-003",

        source="planning",

        memory_type="goal",

        content={

            "target": "station"
        },

        confidence=1.0
    )


    exported = memory.to_dict()


    assert (
        exported["memory_id"]
        == "MEM-003"
    )

    assert (
        exported["source"]
        == "planning"
    )

    assert (
        exported["memory_type"]
        == "goal"
    )

    assert (
        exported["content"]["target"]
        == "station"
    )

    assert (
        exported["confidence"]
        == 1.0
    )

    assert isinstance(
        exported["created_at"],
        datetime
    )


def test_memory_record_default_values():

    memory = MemoryRecord(

        memory_id="MEM-004",

        source="system",

        memory_type="status",

        content={}
    )


    assert (
        memory.confidence
        is None
    )

    assert (
        memory.metadata
        == {}
    )