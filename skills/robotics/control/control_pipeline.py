"""
KALATRACE Robotics Control Pipeline

Coordinates the complete control cycle.

The pipeline integrates:

- ControlManager
- Controllers
- Actuators

It converts high-level movement intentions
into executable control commands.

This layer does not communicate directly
with physical hardware.
"""

from copy import deepcopy



class ControlPipeline:
    """
    Coordinates robotic control execution.
    """



    def __init__(
        self,
        control_manager
    ):

        self.control_manager = control_manager

        self.last_execution = None

        self.active = False



    def execute(
        self,
        controller_id: str,
        command: dict
    ):
        """
        Execute a complete control cycle.
        """


        result = self.control_manager.execute(
            controller_id,
            command
        )


        self.last_execution = deepcopy(
            result
        )


        self.active = True


        return deepcopy(
            result
        )



    def stop(self):
        """
        Stop control execution.
        """

        self.control_manager.stop_all()

        self.active = False



    def get_status(self):
        """
        Return pipeline status.
        """

        return {

            "active":
                self.active,

            "control":
                self.control_manager.get_status()
        }



    def get_last_execution(self):
        """
        Return last executed command.
        """

        return deepcopy(
            self.last_execution
        )



    def clear(self):
        """
        Reset pipeline state.
        """

        self.control_manager.clear()

        self.last_execution = None

        self.active = False



    def export(self):
        """
        Export current control state.
        """

        return {

            "active":
                self.active,

            "last_execution":
                deepcopy(
                    self.last_execution
                ),

            "control_manager":
                self.control_manager.export()
        }