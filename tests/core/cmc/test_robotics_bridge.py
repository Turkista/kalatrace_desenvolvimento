"""
Tests for the CMC <-> Robotics bridge: choosing a robot and
dispatching a mission's command to it.
"""

import pytest

from core.cmc.command_mission_center import CommandMissionCenter
from core.cmc.robotics_bridge import executor_name_for_robot


@pytest.fixture
def cmc_with_robots():

    cmc = CommandMissionCenter()

    cmc.connect_robotics()

    cmc.robotics_skill.register_robot("drone-01")
    cmc.robotics_skill.get_robot_context("drone-01").update_status(
        "connected"
    )

    cmc.robotics_skill.register_robot("drone-02")
    cmc.robotics_skill.get_robot_context("drone-02").update_status(
        "connected"
    )

    return cmc


def test_list_robots_returns_registered_robots(cmc_with_robots):

    robots = cmc_with_robots.list_robots()

    assert set(robots.keys()) == {"drone-01", "drone-02"}
    assert robots["drone-01"]["status"] == "connected"


def test_send_mission_to_robot_dispatches_and_updates_robot(
    cmc_with_robots,
):

    cmc = cmc_with_robots

    mission = cmc.create_mission(
        name="Patrulha Setor A",
        objective="Mapear setor A",
    )

    outcome = cmc.send_mission_to_robot(
        mission_id=mission.mission_id,
        robot_id="drone-01",
        name="voo-patrulha-A",
        objective="Sobrevoar setor A em altitude 40m",
    )

    assert outcome["command"]["status"] == "EXECUTING"
    assert outcome["result"]["success"] is True

    robot_context = cmc.robotics_skill.get_robot_context("drone-01")

    assert robot_context.status == "executing"
    assert robot_context.mission == "Sobrevoar setor A em altitude 40m"

    # drone-02 was never chosen, so it stays untouched.
    other = cmc.robotics_skill.get_robot_context("drone-02")
    assert other.status == "connected"
    assert other.mission is None


def test_send_mission_to_robot_creates_dedicated_executor(
    cmc_with_robots,
):

    cmc = cmc_with_robots

    mission = cmc.create_mission(
        name="Inspecao",
        objective="Inspecionar linha de producao",
    )

    assert not cmc.command_center.dispatcher.has_executor(
        executor_name_for_robot("drone-02")
    )

    cmc.send_mission_to_robot(
        mission_id=mission.mission_id,
        robot_id="drone-02",
        name="inspecao-linha",
        objective="Inspecionar linha 3",
    )

    assert cmc.command_center.dispatcher.has_executor(
        executor_name_for_robot("drone-02")
    )


def test_send_mission_to_unknown_robot_raises(cmc_with_robots):

    cmc = cmc_with_robots

    mission = cmc.create_mission(
        name="Missao X",
        objective="Objetivo X",
    )

    with pytest.raises(ValueError):
        cmc.send_mission_to_robot(
            mission_id=mission.mission_id,
            robot_id="drone-inexistente",
            name="cmd",
            objective="obj",
        )


def test_mission_overview_lists_robot_command(cmc_with_robots):

    cmc = cmc_with_robots

    mission = cmc.create_mission(
        name="Patrulha Setor B",
        objective="Mapear setor B",
    )

    cmc.send_mission_to_robot(
        mission_id=mission.mission_id,
        robot_id="drone-01",
        name="voo-patrulha-B",
        objective="Sobrevoar setor B",
    )

    overview = cmc.mission_overview(mission.mission_id)

    assert len(overview["commands"]) == 1
    assert overview["commands"][0]["objective"] == "Sobrevoar setor B"


def test_connect_robotics_is_idempotent_with_shared_instance(
    cmc_with_robots,
):

    cmc = cmc_with_robots

    shared_skill = cmc.robotics_skill

    other_cmc = CommandMissionCenter()
    other_cmc.connect_robotics(shared_skill)

    assert other_cmc.robotics_skill is shared_skill
    assert "drone-01" in other_cmc.list_robots()
