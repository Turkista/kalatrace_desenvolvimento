"""
KALATRACE Robotics Perception Manager

Coordinates robotic sensors and generated observations.
"""

from copy import deepcopy

from skills.robotics.perception.observation import Observation


class PerceptionManager:
    """
    Coordinates robotic perception.
    """

    def __init__(self, robot_id: str):

        self.robot_id = robot_id

        self.sensors = {}

        self.observations = []

    def register_sensor(self, sensor):

        if sensor.sensor_id in self.sensors:

            raise ValueError(
                "Sensor already registered."
            )

        self.sensors[sensor.sensor_id] = sensor

    def unregister_sensor(self, sensor_id: str):

        self.sensors.pop(sensor_id, None)

    def has_sensor(self, sensor_id: str):

        return sensor_id in self.sensors

    def sensor_count(self):

        return len(self.sensors)

    def activate_sensor(self, sensor_id: str):

        self._get_sensor(sensor_id).activate()

    def deactivate_sensor(self, sensor_id: str):

        self._get_sensor(sensor_id).deactivate()

    def collect_data(
        self,
        sensor_id: str,
        value,
        location=None,
        confidence=None,
        context=None
    ):

        sensor = self._get_sensor(sensor_id)

        reading = sensor.read(value)

        observation = Observation(

            observation_id=f"OBS-{len(self.observations)+1}",

            robot_id=self.robot_id,

            sensor_id=sensor.sensor_id,

            observation_type=sensor.sensor_type,

            value=reading["value"],

            unit=sensor.unit,

            confidence=confidence,

            location=location,

            context=context
        )

        self.observations.append(observation)

        return observation

    def get_observations(self):

        return deepcopy(self.observations)

    def clear(self):

        self.observations.clear()

    def export(self):

        return {

            "robot_id": self.robot_id,

            "sensor_count": self.sensor_count(),

            "observation_count": len(self.observations),

            "sensors": list(self.sensors.keys()),

            "observations": [

                observation.export()

                if hasattr(observation, "export")

                else str(observation)

                for observation in self.observations
            ]
        }

    def get_sensor(self, sensor_id: str):

        return self._get_sensor(sensor_id)

    def _get_sensor(self, sensor_id: str):

        if sensor_id not in self.sensors:

            raise ValueError(
                f"Sensor '{sensor_id}' not found."
            )

        return self.sensors[sensor_id]