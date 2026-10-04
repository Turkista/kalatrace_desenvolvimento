"""
KALATRACE Robotics LiDAR Sensor

Specialized perception sensor responsible
for spatial measurements.

The LiDAR sensor captures distances and
environment geometry.
"""


from skills.robotics.perception.sensor import Sensor



class LidarSensor(Sensor):
    """
    Represents a robotic LiDAR sensor.
    """


    def __init__(
        self,
        sensor_id: str,
        range_limit: float,
        accuracy: float = None,
        scan_rate: int = None,
        manufacturer: str = None
    ):

        super().__init__(

            sensor_id=sensor_id,

            sensor_type="distance",

            unit="meters",

            accuracy=accuracy,

            manufacturer=manufacturer
        )


        self.range_limit = range_limit

        self.scan_rate = scan_rate

        self.points_detected = []



    def measure_distance(
        self,
        distance: float
    ):
        """
        Measure distance to an object.
        """


        if self.status != "active":

            raise RuntimeError(
                "LiDAR sensor is inactive."
            )


        if distance < 0:

            raise ValueError(
                "Distance cannot be negative."
            )


        if distance > self.range_limit:

            raise ValueError(
                "Object outside LiDAR range."
            )


        self.last_value = distance


        measurement = {

            "distance":
                distance,

            "unit":
                self.unit
        }


        self.points_detected.append(
            measurement
        )


        return measurement



    def scan_environment(
        self,
        distances: list
    ):
        """
        Perform environment scan.
        """


        results = []


        for distance in distances:

            results.append(
                self.measure_distance(
                    distance
                )
            )


        return results



    def get_lidar_state(self):
        """
        Return LiDAR specific state.
        """


        state = self.get_state()


        state.update({

            "range_limit":
                self.range_limit,

            "scan_rate":
                self.scan_rate,

            "points_detected":
                len(self.points_detected)
        })


        return state