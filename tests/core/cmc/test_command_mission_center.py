"""
KALATRACE Command & Mission Center Tests

Validates the CMC facade: mission-centric operations that
keep mission, command, decision, and resource state consistent
with each other.
"""

import pytest

from core.cmc import CommandMissionCenter


def test_create_mission():

    cmc = CommandMissionCenter()

    mission = cmc.create_mission(
        name="MEDIKALAT Research Mission",
        objective="Evaluate regenerative hypothesis involving Bakuchiol + Resveratrol",
        priority="HIGH",
    )

    assert mission.name == "MEDIKALAT Research Mission"
    assert mission.status == "CREATED"


def test_issue_command_links_to_mission():

    cmc = CommandMissionCenter()

    mission = cmc.create_mission(
        name="Investigate Hypothesis IEC-154",
        objective="Search contradictory evidence",
    )

    command = cmc.issue_command(
        mission_id=mission.mission_id,
        name="Investigate Hypothesis IEC-154",
        objective="Search contradictory evidence",
        priority="CRITICAL",
    )

    assert command.mission_id == mission.mission_id
    assert command in mission.commands


def test_record_decision_links_to_mission():

    cmc = CommandMissionCenter()

    mission = cmc.create_mission(
        name="Analyze Melasma Treatment Mechanism",
        objective="Generate hypothesis",
    )

    decision = cmc.record_decision(
        mission_id=mission.mission_id,
        action="Prioritize IEC-045",
        reason="3 independent studies + mechanistic compatibility + low contradiction level",
        confidence=0.82,
        evidence=["Liu et al. 2020"],
        alternatives=["Deprioritize"],
    )

    assert decision.mission_id == mission.mission_id
    assert decision in mission.decisions


def test_allocate_and_release_resource_links_to_mission():

    cmc = CommandMissionCenter()

    mission = cmc.create_mission(
        name="Literature Acquisition",
        objective="Acquire papers",
    )

    resource = cmc.resource_allocator.register_resource(
        name="Research Agent Pool",
        total_capacity=3,
        unit="agents",
        resource_type="agent",
    )

    allocation = cmc.allocate_resource(
        mission_id=mission.mission_id,
        resource_id=resource.resource_id,
        amount=1,
    )

    assert allocation in mission.resources
    assert cmc.resource_allocator.available_capacity(resource.resource_id) == 2

    cmc.release_resource(allocation.allocation_id)

    assert cmc.resource_allocator.available_capacity(resource.resource_id) == 3


def test_mission_overview_aggregates_subsystems():

    cmc = CommandMissionCenter()

    mission = cmc.create_mission(
        name="MISSION-001",
        objective="Evaluate regenerative hypothesis",
    )

    cmc.issue_command(
        mission_id=mission.mission_id,
        name="Investigate",
        objective="Search evidence",
    )

    cmc.record_decision(
        mission_id=mission.mission_id,
        action="Prioritize IEC-045",
        reason="Strong evidence",
        confidence=0.8,
    )

    resource = cmc.resource_allocator.register_resource(
        name="Compute",
        total_capacity=10,
        unit="hours",
    )

    cmc.allocate_resource(
        mission_id=mission.mission_id,
        resource_id=resource.resource_id,
        amount=4,
    )

    overview = cmc.mission_overview(mission.mission_id)

    assert overview["mission"]["mission_id"] == mission.mission_id
    assert len(overview["commands"]) == 1
    assert len(overview["decisions"]) == 1
    assert len(overview["resource_allocations"]) == 1
    assert len(overview["timeline"]) > 0


def test_stats_and_health_check():

    cmc = CommandMissionCenter()

    cmc.create_mission(name="M1", objective="O1")

    stats = cmc.stats()

    assert stats["missions"] == 1
    assert "commands" in stats
    assert "decisions" in stats
    assert "resources" in stats

    health = cmc.health_check()

    assert health["command_mission_center"] == "OK"


def test_unknown_mission_raises():

    cmc = CommandMissionCenter()

    with pytest.raises(ValueError):
        cmc.issue_command(
            mission_id="does-not-exist",
            name="X",
            objective="Y",
        )
