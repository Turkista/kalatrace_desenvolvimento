"""
KALATRACE Robotics Actuator

Represents a physical execution component.

The actuator abstraction manages commands
sent to physical devices.

It does not communicate directly with
hardware in the current version.

Future implementations may connect to:

- motors
- servos
- ESC controllers
- robotic joints
"""

from copy import deepcopy



class Actuator:
    """
    Base physical actuator.
    """


    def __init__(
        self,
        actuator_id: str
    ):

        self.actuator_id = actuator_id

        self.state = "idle"

        self.current_command = None

        self.command_history = []

        self.enabled = True



    def activate(
        self,
        command: dict
    ):
        """
        Activate actuator with command.
        """

        if not self.enabled:

            raise RuntimeError(
                "Actuator is disabled."
            )


        self.current_command = deepcopy(
            command
        )


        self.state = "active"


        self.command_history.append(
            deepcopy(command)
        )


        return deepcopy(
            command
        )



    def stop(self):
        """
        Stop actuator operation.
        """

        self.current_command = None

        self.state = "idle"



    def enable(self):
        """
        Enable actuator.
        """

        self.enabled = True



    def disable(self):
        """
        Disable actuator.
        """

        self.enabled = False



    def get_state(self):
        """
        Return actuator state.
        """

        return self.state



    def get_command(self):
        """
        Return current command.
        """

        return deepcopy(
            self.current_command
        )



    def get_history(self):
        """
        Return command history.
        """

        return deepcopy(
            self.command_history
        )



    def clear(self):
        """
        Reset actuator.
        """

        self.state = "idle"

        self.current_command = None

        self.command_history.clear()



    def export(self):
        """
        Export actuator state.
        """

        return {

            "actuator_id":
                self.actuator_id,


            "state":
                self.state,


            "enabled":
                self.enabled,


            "current_command":
                deepcopy(
                    self.current_command
                ),


            "history_size":
                len(
                    self.command_history
                )
        }