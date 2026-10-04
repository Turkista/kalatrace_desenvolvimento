"""
KALATRACE Robotics Battery Sensor

Internal perception sensor responsible
for monitoring robot energy state.

Represents robotic proprioception.
"""


from skills.robotics.perception.sensor import Sensor



class BatterySensor(Sensor):
    """
    Represents a robotic battery monitoring sensor.
    """


    def __init__(
        self,
        sensor_id: str,
        battery_capacity: float,
        accuracy: float = None,
        manufacturer: str = None
    ):

        super().__init__(

            sensor_id=sensor_id,

            sensor_type="battery",

            unit="percentage",

            accuracy=accuracy,

            manufacturer=manufacturer
        )


        self.battery_capacity = (
            battery_capacity
        )

        self.energy_history = []



    def measure_battery(
        self,
        percentage: float
    ):
        """
        Measure current battery level.
        """


        if self.status != "active":

            raise RuntimeError(
                "Battery sensor is inactive."
            )


        if (
            percentage < 0
            or percentage > 100
        ):

            raise ValueError(
                "Battery percentage must be between 0 and 100."
            )


        self.last_value = percentage


        reading = {

            "battery":
                percentage,

            "unit":
                self.unit,

            "capacity":
                self.battery_capacity
        }


        self.energy_history.append(
            reading
        )


        return reading



    def is_low_battery(
        self,
        threshold: float = 20
    ):
        """
        Check if battery is below threshold.
        """


        if self.last_value is None:

            return False


        return (
            self.last_value
            < threshold
        )



    def get_battery_state(self):
        """
        Return battery sensor state.
        """


        state = self.get_state()


        state.update({

            "battery_capacity":
                self.battery_capacity,

            "measurements":
                len(self.energy_history),

            "low_battery":
                self.is_low_battery()
        })


        return state