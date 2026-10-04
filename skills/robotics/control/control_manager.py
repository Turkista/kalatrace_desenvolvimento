"""
KALATRACE Robotics Control Manager

Coordinates robot control operations.

Responsible for managing:

- controllers
- actuators
- control state

Does not communicate directly
with physical hardware.
"""


from copy import deepcopy



class ControlManager:
    """
    Coordinates control execution.
    """



    def __init__(
        self
    ):

        self.controllers = {}

        self.actuators = {}

        self.last_command = None

        self.status = "idle"



    def register_controller(
        self,
        controller_id: str,
        controller
    ):
        """
        Register a controller.
        """

        self.controllers[controller_id] = controller



    def register_actuator(
        self,
        actuator_id: str,
        actuator
    ):
        """
        Register actuator.
        """

        self.actuators[actuator_id] = actuator



    def execute(
        self,
        controller_id: str,
        command: dict
    ):
        """
        Execute control command.
        """

        if controller_id not in self.controllers:

            raise ValueError(
                "Controller not registered."
            )


        result = self.controllers[
            controller_id
        ].execute(
            command
        )


        self.last_command = deepcopy(
            result
        )


        self.status = "executing"


        return result



    def stop_all(self):
        """
        Stop all registered actuators.
        """

        for actuator in self.actuators.values():

            actuator.stop()


        self.status = "stopped"



    def get_status(self):
        """
        Return control status.
        """

        return self.status



    def get_last_command(self):
        """
        Return last command.
        """

        return deepcopy(
            self.last_command
        )



    def clear(self):
        """
        Reset control state.
        """

        self.last_command = None

        self.status = "idle"



    def export(self):
        """
        Export control state.
        """

        return {

            "status":
                self.status,

            "controllers":
                list(
                    self.controllers.keys()
                ),

            "actuators":
                list(
                    self.actuators.keys()
                ),

            "last_command":
                deepcopy(
                    self.last_command
                )
        }