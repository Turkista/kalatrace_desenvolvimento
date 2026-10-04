"""
KALATRACE Robotics Navigation Planner

Responsible for generating navigation paths.

The planner converts a navigation goal
into a sequence of movements.

Current implementation provides a basic
planning abstraction.

Future versions may implement:

- A*
- Dijkstra
- RRT
- probabilistic planning
- AI-based planning
"""


from copy import deepcopy



class Planner:
    """
    Navigation planning engine.
    """


    def __init__(self):

        self.last_plan = None

        self.history = []



    def create_plan(
        self,
        start: dict,
        goal: dict
    ):
        """
        Create a simple navigation plan.

        Current version generates a direct path
        between start and goal.
        """


        plan = {

            "start":
                deepcopy(start),


            "goal":
                deepcopy(goal),


            "waypoints":
                [
                    deepcopy(start),
                    deepcopy(goal)
                ]
        }


        self.last_plan = plan


        self.history.append(
            deepcopy(plan)
        )


        return plan



    def get_last_plan(self):
        """
        Return latest generated plan.
        """

        return deepcopy(
            self.last_plan
        )



    def get_history(self):
        """
        Return planning history.
        """

        return deepcopy(
            self.history
        )



    def clear(self):
        """
        Reset planner state.
        """

        self.last_plan = None

        self.history.clear()



    def export(self):
        """
        Export planner state.
        """

        return {

            "last_plan":
                deepcopy(
                    self.last_plan
                ),

            "history_size":
                len(
                    self.history
                )
        }