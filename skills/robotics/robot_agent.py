"""
KALATRACE Robot Agent

Represents a robotic entity
inside the KALATRACE ecosystem.

A RobotAgent is more than a device.
It contains identity, capabilities
and operational state.
"""


from datetime import datetime, UTC



class RobotAgent:
    """
    Represents a robotic agent.
    """


    def __init__(
        self,
        robot_id: str,
        model: str,
        manufacturer: str = None
    ):

        self.robot_id = robot_id

        self.model = model

        self.manufacturer = manufacturer


        self.status = "offline"


        self.capabilities = []

        self.sensors = []

        self.actuators = []


        self.current_mission = None


        self.created_at = datetime.now(UTC)

        self.updated_at = datetime.now(UTC)



    def connect(self):
        """
        Mark robot as connected.
        """

        self.status = "connected"

        self.updated_at = datetime.now(UTC)



    def disconnect(self):
        """
        Mark robot as disconnected.
        """

        self.status = "offline"

        self.updated_at = datetime.now(UTC)



    def add_capability(
        self,
        capability: str
    ):
        """
        Register a robot capability.
        """

        if capability not in self.capabilities:

            self.capabilities.append(
                capability
            )


    def add_sensor(
        self,
        sensor_name: str
    ):
        """
        Register a sensor.
        """

        if sensor_name not in self.sensors:

            self.sensors.append(
                sensor_name
            )


    def add_actuator(
        self,
        actuator_name: str
    ):
        """
        Register an actuator.
        """

        if actuator_name not in self.actuators:

            self.actuators.append(
                actuator_name
            )



    def assign_mission(
        self,
        mission_name: str
    ):
        """
        Assign an operational mission.
        """

        self.current_mission = mission_name

        self.status = "executing"

        self.updated_at = datetime.now(UTC)



    def get_profile(self):
        """
        Return complete robot profile.
        """

        return {

            "robot_id":
                self.robot_id,

            "model":
                self.model,

            "manufacturer":
                self.manufacturer,

            "status":
                self.status,

            "capabilities":
                self.capabilities,

            "sensors":
                self.sensors,

            "actuators":
                self.actuators,

            "mission":
                self.current_mission
        }