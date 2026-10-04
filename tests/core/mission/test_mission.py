"""
KALATRACE Mission Tests

Validates mission lifecycle management.
"""


from core.mission import (
    Mission,
    MissionRegistry,
    MissionManager,
    MissionState,
    MissionStateMachine,
    MissionTimeline
)



def test_create_mission():

    mission = Mission(
        name="MEDIKALAT Research Mission",
        objective="Evaluate regenerative hypothesis",
        priority="HIGH"
    )


    assert mission.name == (
        "MEDIKALAT Research Mission"
    )

    assert mission.status == "CREATED"



def test_mission_registry():

    registry = MissionRegistry()


    mission = Mission(
        name="Registry Test",
        objective="Validate registry"
    )


    registry.register(
        mission
    )


    assert registry.count() == 1

    assert (
        registry.get(
            mission.mission_id
        )
        ==
        mission
    )



def test_prepare_mission():

    registry = MissionRegistry()

    manager = MissionManager(
        registry
    )


    mission = manager.create_mission(
        name="Preparation Test",
        objective="Validate preparation"
    )


    manager.prepare_mission(
        mission.mission_id
    )


    assert mission.status == "READY"



def test_start_mission():

    registry = MissionRegistry()

    manager = MissionManager(
        registry
    )


    mission = manager.create_mission(
        name="Execution Test",
        objective="Validate execution"
    )


    manager.prepare_mission(
        mission.mission_id
    )


    manager.start_mission(
        mission.mission_id
    )


    assert mission.status == "EXECUTING"



def test_invalid_transition():

    try:

        MissionStateMachine.transition(
            MissionState.CREATED,
            MissionState.COMPLETED
        )

        assert False

    except ValueError:

        assert True



def test_mission_timeline():

    timeline = MissionTimeline()


    timeline.add_event(
        event_type="TEST",
        description="Timeline validation",
        source="pytest"
    )


    assert timeline.count() == 1

    assert (
        timeline.latest()
        .event_type
        ==
        "TEST"
    )



def test_complete_mission_flow():

    registry = MissionRegistry()

    manager = MissionManager(
        registry
    )


    mission = manager.create_mission(
        name="Full Lifecycle Test",
        objective="Validate complete flow"
    )


    manager.prepare_mission(
        mission.mission_id
    )


    manager.start_mission(
        mission.mission_id
    )


    manager.wait_analysis(
        mission.mission_id
    )


    manager.validate_mission(
        mission.mission_id
    )


    manager.complete_mission(
        mission.mission_id
    )


    assert mission.status == "COMPLETED"