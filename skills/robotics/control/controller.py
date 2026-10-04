"""
KALATRACE Robotics Controller

Base controller responsible for converting
high-level navigation decisions into low-level
control commands.

This class does not communicate directly
with hardware.

Future specialized controllers include:

- VelocityController
- FlightController
- ArmController
- WheelController
- ManipulatorController
"""

from copy import deepcopy


class Controller:
    """
    Base robotics controller.
    """

    def __init__(self):

        self.current_command = None

        self.command_history = []

        self.enabled = True

    def execute(
        self,
        command: dict
    ):
        """
        Execute a control command.

        Current implementation only stores
        the command.

        Future implementations will forward
        commands to specialized controllers.
        """

        if not self.enabled:

            raise RuntimeError(
                "Controller is disabled."
            )

        self.current_command = deepcopy(
            command
        )

        self.command_history.append(
            deepcopy(command)
        )

        return deepcopy(command)

    def get_current_command(self):
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

    def enable(self):
        """
        Enable controller.
        """

        self.enabled = True

    def disable(self):
        """
        Disable controller.
        """

        self.enabled = False

    def clear(self):
        """
        Reset runtime state.
        """

        self.current_command = None

        self.command_history.clear()

    def export(self):
        """
        Export controller state.
        """

        return {

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