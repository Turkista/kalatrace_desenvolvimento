"""
KALATRACE Robotics Velocity Controller

Controls movement commands based on velocity.

This component translates navigation
decisions into velocity targets.

It does not communicate directly
with motors or hardware.
"""


from copy import deepcopy

from .controller import Controller



class VelocityController(Controller):
    """
    Velocity based motion controller.
    """


    def __init__(self):

        super().__init__()

        self.velocity = {

            "linear": 0,

            "angular": 0
        }



    def set_velocity(
        self,
        linear: float,
        angular: float
    ):
        """
        Define velocity target.
        """

        command = {

            "type": "velocity",

            "linear": linear,

            "angular": angular
        }


        self.velocity = {

            "linear": linear,

            "angular": angular
        }


        return self.execute(
            command
        )



    def get_velocity(self):
        """
        Return current velocity.
        """

        return deepcopy(
            self.velocity
        )



    def stop(self):
        """
        Stop movement.
        """

        return self.set_velocity(
            linear=0,
            angular=0
        )



    def export(self):
        """
        Export velocity controller state.
        """

        data = super().export()


        data.update(
            {

                "velocity":
                    deepcopy(
                        self.velocity
                    )
            }
        )


        return data