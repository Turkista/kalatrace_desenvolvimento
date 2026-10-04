"""
KALATRACE Robotics Sensor Tests

Validates the base robotic sensor model.

Tests:

- Sensor creation
- Sensor activation
- Measurement acquisition
- State reporting
"""


from skills.robotics.perception.sensor import Sensor



def create_temperature_sensor():

    sensor = Sensor(
        sensor_id="TEMP-001",
        sensor_type="temperature",
        unit="celsius",
        accuracy=0.98,
        manufacturer="KALATRACE Sensors"
    )

    return sensor



def test_sensor_creation():

    sensor = create_temperature_sensor()


    assert sensor.sensor_id == "TEMP-001"

    assert sensor.sensor_type == "temperature"

    assert sensor.unit == "celsius"

    assert sensor.accuracy == 0.98

    assert sensor.status == "inactive"



def test_sensor_activation():

    sensor = create_temperature_sensor()


    sensor.activate()


    assert (
        sensor.status
        == "active"
    )



def test_sensor_reading():

    sensor = create_temperature_sensor()


    sensor.activate()


    reading = sensor.read(
        37.5
    )


    assert (
        reading["sensor_id"]
        == "TEMP-001"
    )


    assert (
        reading["value"]
        == 37.5
    )


    assert (
        reading["unit"]
        == "celsius"
    )



def test_sensor_last_value():

    sensor = create_temperature_sensor()


    sensor.activate()


    sensor.read(
        36.8
    )


    assert (
        sensor.last_value
        == 36.8
    )


def test_sensor_state():

    sensor = create_temperature_sensor()


    sensor.activate()


    sensor.read(
        37.2
    )


    state = sensor.get_state()


    assert (
        state["sensor_id"]
        == "TEMP-001"
    )


    assert (
        state["status"]
        == "active"
    )


    assert (
        state["last_value"]
        == 37.2
    )