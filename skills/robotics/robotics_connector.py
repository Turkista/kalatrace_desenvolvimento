"""
KALATRACE Robotics Connector

Communication layer between physical
robotic agents and the Robotics Skill.

Responsible for:
- connection handling
- telemetry transmission
- command receiving

It does not process knowledge.
It only transports information.
"""


from datetime import datetime



class RoboticsConnector:
    """
    Represents a communication channel
    with a robotic agent.
    """


    def __init__(
        self,
        robot_id: str,
        api
    ):

        self.robot_id = robot_id

        self.api = api

        self.connected = False

        self.last_message = None



    def connect(
        self,
        metadata: dict = None
    ):
        """
        Establish robot connection.
        """


        result = self.api.connect_robot(
            self.robot_id,
            metadata
        )


        self.connected = True


        return result



    def disconnect(self):
        """
        Close robot connection.
        """


        result = self.api.disconnect_robot(
            self.robot_id
        )


        self.connected = False


        return result



    def send_sensor_data(
        self,
        sensor_name: str,
        value
    ):
        """
        Send telemetry data
        from robot to KALATRACE.
        """


        if not self.connected:

            raise RuntimeError(
                "Robot is not connected."
            )


        self.last_message = datetime.now()


        return self.api.update_sensor(
            self.robot_id,
            sensor_name,
            value
        )



    def start_task(
        self,
        task_name: str
    ):
        """
        Request a robotic mission.
        """


        if not self.connected:

            raise RuntimeError(
                "Robot is not connected."
            )


        return self.api.start_mission(
            self.robot_id,
            task_name
        )



    def get_state(self):
        """
        Retrieve current robot state.
        """


        return self.api.get_robot(
            self.robot_id
        )