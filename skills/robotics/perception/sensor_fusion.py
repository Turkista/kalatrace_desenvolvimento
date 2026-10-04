"""
KALATRACE Robotics Sensor Fusion

Responsible for combining information from
multiple robotic sensors into a unified
perception.

Sensor Fusion does not communicate directly
with hardware.

Its responsibility is to aggregate sensor
readings into a single perception snapshot.
"""

from copy import deepcopy


class SensorFusion:
    """
    Multi-sensor fusion engine.
    """

    def __init__(self):

        self.sensors = {}

        self.latest_readings = {}

        self.last_fusion = None

        self.fusion_history = []

    def register_sensor(
        self,
        sensor
    ):
        """
        Register a sensor.
        """

        self.sensors[
            sensor.sensor_id
        ] = sensor

    def unregister_sensor(
        self,
        sensor_id: str
    ):
        """
        Remove a sensor.
        """

        if sensor_id in self.sensors:

            del self.sensors[sensor_id]

        self.latest_readings.pop(
            sensor_id,
            None
        )

    def update_reading(
        self,
        sensor_id: str,
        reading
    ):
        """
        Update latest reading from a sensor.
        """

        if sensor_id not in self.sensors:

            raise ValueError(
                f"Unknown sensor '{sensor_id}'."
            )

        self.latest_readings[
            sensor_id
        ] = reading

    def collect(self):
        """
        Return all current readings.
        """

        return deepcopy(
            self.latest_readings
        )

    def validate(self):
        """
        Basic validation.

        Returns True if at least one sensor
        produced data.
        """

        return (
            len(self.latest_readings) > 0
        )

    def fuse(self):
        """
        Build a unified perception.

        The current version simply aggregates
        sensor outputs.

        Future versions may perform:
            - probabilistic fusion
            - Bayesian inference
            - confidence weighting
            - temporal filtering
            - AI-based fusion
        """

        if not self.validate():

            raise RuntimeError(
                "No sensor data available."
            )

        fusion = {

            "sensor_count":
                len(self.latest_readings),

            "readings":
                deepcopy(
                    self.latest_readings
                )
        }

        self.last_fusion = fusion

        self.fusion_history.append(
            deepcopy(fusion)
        )

        return fusion

    def build_observation(self):
        """
        Convert the latest fusion into
        an observation payload.

        Future versions will instantiate
        the Observation class directly.
        """

        if self.last_fusion is None:

            raise RuntimeError(
                "No fusion available."
            )

        return {

            "type":
                "sensor_fusion",

            "data":
                deepcopy(
                    self.last_fusion
                )
        }

    def get_last_fusion(self):
        """
        Return latest fusion.
        """

        return deepcopy(
            self.last_fusion
        )

    def history(self):
        """
        Return fusion history.
        """

        return deepcopy(
            self.fusion_history
        )

    def clear(self):
        """
        Reset all runtime information.
        """

        self.latest_readings.clear()

        self.last_fusion = None

        self.fusion_history.clear()