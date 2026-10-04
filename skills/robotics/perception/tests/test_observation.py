"""
KALATRACE Robotics Observation Tests

Validates the transformation of raw
sensor measurements into contextualized
robotic observations.

Tests:

- Observation creation
- Robot and sensor association
- Measurement data
- Confidence information
- Context storage
- Dictionary conversion
"""


from skills.robotics.perception.observation import Observation



def create_temperature_observation():

    observation = Observation(

        observation_id="OBS-001",

        robot_id="LAB-001",

        sensor_id="TEMP-001",

        observation_type="temperature",

        value=37.5,

        unit="celsius",

        confidence=0.98,

        location="robot_arm",

        context={
            "experiment": "sample_analysis"
        }
    )


    return observation



def test_observation_creation():

    observation = (
        create_temperature_observation()
    )


    assert (
        observation.observation_id
        == "OBS-001"
    )


    assert (
        observation.robot_id
        == "LAB-001"
    )


    assert (
        observation.sensor_id
        == "TEMP-001"
    )



def test_observation_measurement():

    observation = (
        create_temperature_observation()
    )


    assert (
        observation.value
        == 37.5
    )


    assert (
        observation.unit
        == "celsius"
    )


    assert (
        observation.observation_type
        == "temperature"
    )



def test_observation_confidence():

    observation = (
        create_temperature_observation()
    )


    assert (
        observation.confidence
        == 0.98
    )



def test_observation_location():

    observation = (
        create_temperature_observation()
    )


    assert (
        observation.location
        == "robot_arm"
    )



def test_observation_context():

    observation = (
        create_temperature_observation()
    )


    assert (
        observation.context["experiment"]
        == "sample_analysis"
    )



def test_observation_to_dict():

    observation = (
        create_temperature_observation()
    )


    data = observation.to_dict()


    assert (
        data["observation_id"]
        == "OBS-001"
    )


    assert (
        data["value"]
        == 37.5
    )


    assert (
        data["confidence"]
        == 0.98
    )


    assert (
        data["context"]["experiment"]
        == "sample_analysis"
    )