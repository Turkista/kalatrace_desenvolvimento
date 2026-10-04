"""
KALATRACE Robotics Sensor Model

Represents a physical sensor
connected to a robotic agent.

A sensor is responsible for
capturing measurements from
the physical environment.
"""


from datetime import datetime, UTC



class Sensor:
    """
    Base model for robotic sensors.
    """


    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        unit: str,
        accuracy: float = None,
        manufacturer: str = None
    ):

        self.sensor_id = sensor_id

        self.sensor_type = sensor_type

        self.unit = unit

        self.accuracy = accuracy

        self.manufacturer = manufacturer


        self.status = "inactive"


        self.last_value = None

        self.last_reading_at = None



    def activate(self):
        """
        Activate sensor.
        """

        self.status = "active"



    def deactivate(self):
        """
        Deactivate sensor.
        """

        self.status = "inactive"



    def read(
        self,
        value
    ):
        """
        Register a sensor measurement.
        """


        if self.status != "active":

            raise RuntimeError(
                "Sensor is inactive."
            )


        self.last_value = value


        self.last_reading_at = (
            datetime.now(UTC)
        )


        return {

            "sensor_id":
                self.sensor_id,

            "value":
                value,

            "unit":
                self.unit,

            "timestamp":
                self.last_reading_at
        }



    def get_state(self):
        """
        Return current sensor state.
        """

        return {

            "sensor_id":
                self.sensor_id,

            "type":
                self.sensor_type,

            "unit":
                self.unit,

            "accuracy":
                self.accuracy,

            "manufacturer":
                self.manufacturer,

            "status":
                self.status,

            "last_value":
                self.last_value,

            "last_reading_at":
                self.last_reading_at
        }