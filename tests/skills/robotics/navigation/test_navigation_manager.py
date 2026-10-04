"""
KALATRACE Robotics Navigation Manager Tests

Tests navigation coordination.
"""


from skills.robotics.navigation.planner import Planner
from skills.robotics.navigation.navigation_manager import NavigationManager



def create_manager():
    """
    Helper function.
    """

    planner = Planner()

    manager = NavigationManager(
        planner
    )

    return manager



def test_navigation_manager_creation():
    """
    Test initialization.
    """

    manager = create_manager()


    assert manager.status == "idle"

    assert manager.current_goal is None

    assert manager.current_route is None



def test_set_goal():
    """
    Test goal definition.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 10,
            "y": 20,
            "z": 5
        }
    )


    assert manager.current_goal["x"] == 10

    assert manager.status == "goal_defined"



def test_plan_generation():
    """
    Test route planning.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 50,
            "y": 50,
            "z": 10
        }
    )


    plan = manager.plan(
        {
            "x": 0,
            "y": 0,
            "z": 0
        }
    )


    assert plan["goal"]["x"] == 50

    assert manager.status == "planned"

    assert manager.current_route is not None



def test_start_navigation():
    """
    Test navigation execution start.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 5
        }
    )


    manager.plan(
        {
            "x": 0
        }
    )


    manager.start_navigation()


    assert manager.status == "executing"



def test_stop_navigation():
    """
    Test navigation stop.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 5
        }
    )


    manager.plan(
        {
            "x": 0
        }
    )


    manager.start_navigation()

    manager.stop_navigation()


    assert manager.status == "stopped"



def test_get_route():
    """
    Test route retrieval.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 10
        }
    )


    manager.plan(
        {
            "x": 0
        }
    )


    route = manager.get_route()


    assert route is not None

    assert route["start"]["x"] == 0



def test_navigation_export():
    """
    Test state export.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 100
        }
    )


    data = manager.export()


    assert data["status"] == "goal_defined"

    assert data["goal"]["x"] == 100



def test_navigation_clear():
    """
    Test reset.
    """

    manager = create_manager()


    manager.set_goal(
        {
            "x": 10
        }
    )


    manager.clear()


    assert manager.status == "idle"

    assert manager.current_goal is None

    assert manager.current_route is None