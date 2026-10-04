"""
KALATRACE Robotics Navigation Planner Tests

Tests the navigation planner engine.
"""


from skills.robotics.navigation.planner import Planner



def test_planner_creation():
    """
    Test planner initialization.
    """

    planner = Planner()


    assert planner.last_plan is None

    assert len(planner.history) == 0



def test_create_plan():
    """
    Test basic plan generation.
    """

    planner = Planner()


    plan = planner.create_plan(
        start={
            "x": 0,
            "y": 0,
            "z": 0
        },
        goal={
            "x": 10,
            "y": 20,
            "z": 5
        }
    )


    assert plan["start"]["x"] == 0

    assert plan["goal"]["x"] == 10

    assert len(plan["waypoints"]) == 2



def test_last_plan():
    """
    Test retrieving last plan.
    """

    planner = Planner()


    planner.create_plan(
        start={
            "x": 1
        },
        goal={
            "x": 5
        }
    )


    last = planner.get_last_plan()


    assert last["start"]["x"] == 1

    assert last["goal"]["x"] == 5



def test_planner_history():
    """
    Test planning history.
    """

    planner = Planner()


    planner.create_plan(
        start={
            "x": 0
        },
        goal={
            "x": 1
        }
    )


    planner.create_plan(
        start={
            "x": 1
        },
        goal={
            "x": 2
        }
    )


    history = planner.get_history()


    assert len(history) == 2



def test_planner_export():
    """
    Test planner export.
    """

    planner = Planner()


    planner.create_plan(
        start={
            "x": 0
        },
        goal={
            "x": 10
        }
    )


    data = planner.export()


    assert data["last_plan"] is not None

    assert data["history_size"] == 1



def test_planner_clear():
    """
    Test planner reset.
    """

    planner = Planner()


    planner.create_plan(
        start={
            "x": 0
        },
        goal={
            "x": 10
        }
    )


    planner.clear()


    assert planner.last_plan is None

    assert len(planner.history) == 0