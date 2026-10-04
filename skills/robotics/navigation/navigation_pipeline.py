"""
KALATRACE Robotics Navigation Pipeline

Coordinates the complete navigation flow.

The pipeline integrates:

- Localization
- NavigationManager
- Planner

The pipeline does not control motors
or hardware.

Its responsibility is to coordinate
navigation decisions.
"""


from copy import deepcopy



class NavigationPipeline:
    """
    Coordinates navigation execution.
    """



    def __init__(
        self,
        localization,
        navigation_manager
    ):

        self.localization = localization

        self.navigation_manager = navigation_manager



    def set_goal(
        self,
        goal: dict
    ):
        """
        Define navigation objective.
        """

        self.navigation_manager.set_goal(
            goal
        )



    def process(self):
        """
        Execute one navigation cycle.

        Gets current robot position
        and generates navigation plan.
        """


        position = (
            self.localization.get_pose()
        )


        if position is None:

            raise RuntimeError(
                "Robot position unavailable."
            )


        plan = self.navigation_manager.plan(
            position
        )


        return {

            "position":
                deepcopy(position),


            "plan":
                deepcopy(plan),


            "status":
                self.navigation_manager.get_status()
        }



    def start(self):
        """
        Start navigation.
        """

        self.navigation_manager.start_navigation()



    def stop(self):
        """
        Stop navigation.
        """

        self.navigation_manager.stop_navigation()



    def status(self):
        """
        Return navigation status.
        """

        return self.navigation_manager.get_status()



    def clear(self):
        """
        Reset navigation.
        """

        self.navigation_manager.clear()



    def export(self):
        """
        Export navigation state.
        """

        return {

            "navigation":
                self.navigation_manager.export()
        }