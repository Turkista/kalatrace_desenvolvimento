"""
KALATRACE Robotics Force Sensor Tests

Validates the tactile perception sensor.

Tests:

- Force sensor creation
- Sensor activation
- Force measurement
- Force range validation
- Contact detection
- Contact history
- Force state reporting
"""


from skills.robotics.perception.sensors.force_sensor import (
    ForceSensor
)



def create_force_sensor():

    sensor = ForceSensor(

        sensor_id="FORCE-001",

        force_range=(0, 100),

        resolution=0.01,

        accuracy=0.98,

        manufacturer="KALATRACE Tactile"
    )

    return sensor



def test_force_sensor_creation():

    sensor = create_force_sensor()


    assert (
        sensor.sensor_id
        == "FORCE-001"
    )


    assert (
        sensor.sensor_type
        == "force"
    )


    assert (
        sensor.unit
        == "newton"
    )


    assert (
        sensor.force_range
        == (0, 100)
    )


    assert (
        sensor.status
        == "inactive"
    )



def test_force_sensor_activation():

    sensor = create_force_sensor()


    sensor.activate()


    assert (
        sensor.status
        == "active"
    )



def test_force_measurement():

    sensor = create_force_sensor()


    sensor.activate()


    reading = sensor.measure_force(
        12.5
    )


    assert (
        reading["force"]
        == 12.5
    )


    assert (
        reading["unit"]
        == "newton"
    )


    assert (
        reading["contact"]
        is True
    )


    assert (
        sensor.last_value
        == 12.5
    )



def test_force_range_validation():

    sensor = create_force_sensor()


    sensor.activate()


    try:

        sensor.measure_force(
            150
        )

        assert False


    except ValueError:

        assert True



def test_contact_detection():

    sensor = create_force_sensor()


    sensor.activate()


    sensor.measure_force(
        5
    )


    assert (
        sensor.detect_contact()
        is True
    )



def test_contact_history():

    sensor = create_force_sensor()


    sensor.activate()


    sensor.measure_force(
        5
    )


    sensor.measure_force(
        10
    )


    assert (
        len(sensor.contacts)
        == 2
    )


    assert (
        sensor.contacts[1]["force"]
        == 10
    )



def test_force_sensor_state():

    sensor = create_force_sensor()


    sensor.activate()


    sensor.measure_force(
        20
    )


    state = (
        sensor.get_force_state()
    )


    assert (
        state["sensor_id"]
        == "FORCE-001"
    )


    assert (
        state["resolution"]
        == 0.01
    )


    assert (
        state["contacts_detected"]
        == 1
    )


    assert (
        state["last_value"]
        == 20
    )