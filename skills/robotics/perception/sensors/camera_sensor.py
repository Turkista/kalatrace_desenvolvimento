"""
KALATRACE Robotics Camera Sensor

Specialized perception sensor responsible
for visual data acquisition.

A camera sensor generates image-based
measurements that can later be processed
by computer vision modules.
"""


from skills.robotics.perception.sensor import Sensor



class CameraSensor(Sensor):
    """
    Represents a robotic vision sensor.
    """


    def __init__(
        self,
        sensor_id: str,
        resolution: str,
        frame_rate: int = None,
        accuracy: float = None,
        manufacturer: str = None
    ):

        super().__init__(

            sensor_id=sensor_id,

            sensor_type="vision",

            unit="image",

            accuracy=accuracy,

            manufacturer=manufacturer
        )


        self.resolution = resolution

        self.frame_rate = frame_rate

        self.frames_captured = 0



    def capture_frame(
        self,
        image_data
    ):
        """
        Capture a visual frame.

        image_data can represent:
        - image path
        - image bytes
        - encoded image
        - processed frame
        """


        if self.status != "active":

            raise RuntimeError(
                "Camera sensor is inactive."
            )


        self.frames_captured += 1


        self.last_value = image_data


        return {

            "sensor_id":
                self.sensor_id,

            "type":
                "image",

            "resolution":
                self.resolution,

            "frame_number":
                self.frames_captured,

            "data":
                image_data
        }



    def get_camera_state(self):
        """
        Return camera-specific state.
        """


        state = self.get_state()


        state.update({

            "resolution":
                self.resolution,

            "frame_rate":
                self.frame_rate,

            "frames_captured":
                self.frames_captured
        })


        return state