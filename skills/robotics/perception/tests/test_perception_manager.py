"""
KALATRACE Robotics Perception Manager Tests

Validates the management of robotic
sensors and perception flow.

Tests:

- Sensor registration
- Sensor activation
- Data collection
- Observation generation
- Observation history
"""


from skills.robotics.perception.sensor import Sensor

from skills.robotics.perception.perception_manager import (
    PerceptionManager
)



def create_manager():

    manager = PerceptionManager(
        "LAB-001"
    )

    return manager



def create_temperature_sensor():

    sensor = Sensor(

        sensor_id="TEMP-001",

        sensor_type="temperature",

        unit="celsius",

        accuracy=0.98
    )


    return sensor



def test_sensor_registration():

    manager = create_manager()

    sensor = create_temperature_sensor()


    manager.register_sensor(
        sensor
    )


    assert (
        "TEMP-001"
        in manager.sensors
    )



def test_sensor_activation():

    manager = create_manager()

    sensor = create_temperature_sensor()


    manager.register_sensor(
        sensor
    )


    manager.activate_sensor(
        "TEMP-001"
    )


    assert (
        sensor.status
        == "active"
    )



def test_collect_sensor_data():

    manager = create_manager()

    sensor = create_temperature_sensor()


    manager.register_sensor(
        sensor
    )


    manager.activate_sensor(
        "TEMP-001"
    )


    observation = manager.collect_data(

        "TEMP-001",

        37.5,

        location="robot_arm",

        confidence=0.98
    )


    assert (
        observation.robot_id
        == "LAB-001"
    )


    assert (
        observation.sensor_id
        == "TEMP-001"
    )


    assert (
        observation.value
        == 37.5
    )



def test_observation_creation():

    manager = create_manager()

    sensor = create_temperature_sensor()


    manager.register_sensor(
        sensor
    )


    manager.activate_sensor(
        "TEMP-001"
    )


    observation = manager.collect_data(

        "TEMP-001",

        36.8,

        context={
            "experiment":
            "sample_analysis"
        }
    )


    assert (
        observation.context["experiment"]
        == "sample_analysis"
    )



def test_observation_history():

    manager = create_manager()

    sensor = create_temperature_sensor()


    manager.register_sensor(
        sensor
    )


    manager.activate_sensor(
        "TEMP-001"
    )


    manager.collect_data(
        "TEMP-001",
        36.5
    )


    manager.collect_data(
        "TEMP-001",
        37.0
    )


    observations = (
        manager.get_observations()
    )


    assert (
        len(observations)
        == 2
    )