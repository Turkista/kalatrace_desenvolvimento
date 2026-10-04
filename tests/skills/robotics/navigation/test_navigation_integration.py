"""
KALATRACE Robotics Navigation Integration Tests

Tests the complete navigation cycle.
"""


from skills.robotics.navigation.planner import Planner
from skills.robotics.navigation.navigation_manager import NavigationManager
from skills.robotics.navigation.navigation_pipeline import NavigationPipeline



class MockLocalization:
    """
    Simulates localization provider.
    """


    def __init__(self):

        self.pose = {

            "x": 0,

            "y": 0,

            "z": 0
        }


    def get_pose(self):

        return self.pose



def create_navigation_system():
    """
    Build complete navigation system.
    """

    localization = MockLocalization()

    planner = Planner()

    manager = NavigationManager(
        planner
    )

    pipeline = NavigationPipeline(
        localization,
        manager
    )

    return manager, pipeline



def test_complete_navigation_cycle():
    """
    Test full navigation execution.
    """

    manager, pipeline = create_navigation_system()


    pipeline.set_goal(
        {
            "x": 50,
            "y": 20,
            "z": 10
        }
    )


    result = pipeline.process()


    assert result["plan"] is not None

    assert (
        result["plan"]["goal"]["x"]
        == 50
    )


    pipeline.start()


    assert (
        pipeline.status()
        == "executing"
    )



def test_navigation_state_persistence():
    """
    Test navigation state preservation.
    """

    manager, pipeline = create_navigation_system()


    pipeline.set_goal(
        {
            "x": 100
        }
    )


    pipeline.process()


    exported = pipeline.export()


    assert (
        exported["navigation"]["goal"]["x"]
        == 100
    )



    assert (
        manager.current_route
        is not None
    )



def test_navigation_clear_cycle():
    """
    Test complete reset.
    """

    manager, pipeline = create_navigation_system()


    pipeline.set_goal(
        {
            "x": 30
        }
    )


    pipeline.process()


    pipeline.start()


    pipeline.clear()


    assert (
        pipeline.status()
        == "idle"
    )


    assert (
        manager.current_goal
        is None
    )


    assert (
        manager.current_route
        is None
    )