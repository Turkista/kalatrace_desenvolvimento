"""
KALATRACE Robotics Force Sensor

Specialized perception sensor responsible
for measuring physical interaction forces.

Represents robotic tactile perception.
"""


from skills.robotics.perception.sensor import Sensor



class ForceSensor(Sensor):
    """
    Represents a robotic tactile sensor.
    """


    def __init__(
        self,
        sensor_id: str,
        force_range: tuple,
        resolution: float = None,
        accuracy: float = None,
        manufacturer: str = None
    ):

        super().__init__(

            sensor_id=sensor_id,

            sensor_type="force",

            unit="newton",

            accuracy=accuracy,

            manufacturer=manufacturer
        )


        self.force_range = force_range

        self.resolution = resolution

        self.contacts = []



    def measure_force(
        self,
        force: float
    ):
        """
        Measure applied physical force.
        """


        if self.status != "active":

            raise RuntimeError(
                "Force sensor is inactive."
            )


        minimum, maximum = (
            self.force_range
        )


        if (
            force < minimum
            or force > maximum
        ):

            raise ValueError(
                "Force outside sensor range."
            )


        self.last_value = force


        contact = {

            "force":
                force,

            "unit":
                self.unit,

            "contact":
                force > 0
        }


        self.contacts.append(
            contact
        )


        return contact



    def detect_contact(self):
        """
        Check if physical contact exists.
        """


        if self.last_value is None:

            return False


        return self.last_value > 0



    def get_force_state(self):
        """
        Return force sensor state.
        """


        state = self.get_state()


        state.update({

            "force_range":
                self.force_range,

            "resolution":
                self.resolution,

            "contacts_detected":
                len(self.contacts)
        })


        return state