"""
KALATRACE Robotics Thermal Sensor

Specialized perception sensor responsible
for thermal measurements.

The sensor captures temperature data from
the environment or robotic components.
"""


from skills.robotics.perception.sensor import Sensor



class ThermalSensor(Sensor):
    """
    Represents a robotic thermal sensor.
    """


    def __init__(
        self,
        sensor_id: str,
        temperature_range: tuple,
        resolution: float = None,
        accuracy: float = None,
        manufacturer: str = None
    ):

        super().__init__(

            sensor_id=sensor_id,

            sensor_type="temperature",

            unit="celsius",

            accuracy=accuracy,

            manufacturer=manufacturer
        )


        self.temperature_range = (
            temperature_range
        )

        self.resolution = resolution

        self.measurements = []



    def measure_temperature(
        self,
        temperature: float
    ):
        """
        Capture a thermal measurement.
        """


        if self.status != "active":

            raise RuntimeError(
                "Thermal sensor is inactive."
            )


        minimum, maximum = (
            self.temperature_range
        )


        if (
            temperature < minimum
            or temperature > maximum
        ):

            raise ValueError(
                "Temperature outside sensor range."
            )


        self.last_value = temperature


        self.measurements.append(
            temperature
        )


        return {

            "sensor_id":
                self.sensor_id,

            "temperature":
                temperature,

            "unit":
                self.unit
        }



    def get_thermal_state(self):
        """
        Return thermal sensor state.
        """


        state = self.get_state()


        state.update({

            "temperature_range":
                self.temperature_range,

            "resolution":
                self.resolution,

            "measurements_count":
                len(self.measurements)
        })


        return state