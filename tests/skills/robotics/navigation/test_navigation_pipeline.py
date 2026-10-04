"""
KALATRACE Robotics Navigation Pipeline Tests

Tests complete navigation coordination.
"""


from skills.robotics.navigation.planner import Planner
from skills.robotics.navigation.navigation_manager import NavigationManager
from skills.robotics.navigation.navigation_pipeline import NavigationPipeline



class MockLocalization:
    """
    Simple localization simulator.
    """


    def __init__(self):

        self.pose = {

            "x": 0,

            "y": 0,

            "z": 0
        }



    def get_pose(self):

        return self.pose




def create_pipeline():

    localization = MockLocalization()

    planner = Planner()

    manager = NavigationManager(
        planner
    )

    pipeline = NavigationPipeline(
        localization,
        manager
    )

    return pipeline



def test_navigation_pipeline_creation():
    """
    Test pipeline initialization.
    """

    pipeline = create_pipeline()


    assert pipeline.status() == "idle"



def test_navigation_goal_and_plan():
    """
    Test goal definition and planning.
    """

    pipeline = create_pipeline()


    pipeline.set_goal(
        {
            "x": 20,
            "y": 30,
            "z": 5
        }
    )


    result = pipeline.process()


    assert result["plan"] is not None

    assert result["plan"]["goal"]["x"] == 20

    assert result["status"] == "planned"



def test_navigation_start_stop():
    """
    Test execution control.
    """

    pipeline = create_pipeline()


    pipeline.set_goal(
        {
            "x": 10
        }
    )


    pipeline.process()


    pipeline.start()


    assert pipeline.status() == "executing"


    pipeline.stop()


    assert pipeline.status() == "stopped"



def test_navigation_export():
    """
    Test state export.
    """

    pipeline = create_pipeline()


    pipeline.set_goal(
        {
            "x": 100
        }
    )


    data = pipeline.export()


    assert (
        data["navigation"]["status"]
        == "goal_defined"
    )



def test_navigation_clear():
    """
    Test reset cycle.
    """

    pipeline = create_pipeline()


    pipeline.set_goal(
        {
            "x": 50
        }
    )


    pipeline.clear()


    assert pipeline.status() == "idle"