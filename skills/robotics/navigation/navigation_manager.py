"""
KALATRACE Robotics Navigation Manager

Coordinates navigation activities.

Responsible for managing:

- current route
- navigation status
- active goal
- planner integration
"""


from copy import deepcopy



class NavigationManager:
    """
    Coordinates robot navigation state.
    """


    def __init__(
        self,
        planner
    ):

        self.planner = planner

        self.current_route = None

        self.current_goal = None

        self.status = "idle"



    def set_goal(
        self,
        goal: dict
    ):
        """
        Define navigation target.
        """

        self.current_goal = deepcopy(
            goal
        )

        self.status = "goal_defined"



    def plan(
        self,
        current_position: dict
    ):
        """
        Generate navigation plan.
        """

        if self.current_goal is None:

            raise RuntimeError(
                "No navigation goal defined."
            )


        plan = self.planner.create_plan(
            start=current_position,
            goal=self.current_goal
        )


        self.current_route = deepcopy(
            plan
        )


        self.status = "planned"


        return plan



    def start_navigation(self):
        """
        Start navigation execution.
        """

        if self.current_route is None:

            raise RuntimeError(
                "No route available."
            )


        self.status = "executing"



    def stop_navigation(self):
        """
        Stop current navigation.
        """

        self.status = "stopped"



    def get_status(self):
        """
        Return navigation state.
        """

        return self.status



    def get_route(self):
        """
        Return current route.
        """

        return deepcopy(
            self.current_route
        )



    def clear(self):
        """
        Reset navigation.
        """

        self.current_route = None

        self.current_goal = None

        self.status = "idle"



    def export(self):
        """
        Export navigation state.
        """

        return {

            "status":
                self.status,

            "goal":
                deepcopy(
                    self.current_goal
                ),

            "route":
                deepcopy(
                    self.current_route
                )
        }