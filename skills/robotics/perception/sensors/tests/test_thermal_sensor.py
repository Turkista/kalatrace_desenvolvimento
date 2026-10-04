"""
KALATRACE Robotics Thermal Sensor Tests

Validates the thermal perception sensor.

Tests:

- Thermal sensor creation
- Sensor activation
- Temperature measurement
- Temperature range validation
- Measurement history
- Thermal state reporting
"""


from skills.robotics.perception.sensors.thermal_sensor import (
    ThermalSensor
)



def create_thermal_sensor():

    sensor = ThermalSensor(

        sensor_id="THERM-001",

        temperature_range=(-20, 120),

        resolution=0.1,

        accuracy=0.97,

        manufacturer="KALATRACE Thermal"
    )

    return sensor



def test_thermal_sensor_creation():

    sensor = create_thermal_sensor()


    assert (
        sensor.sensor_id
        == "THERM-001"
    )


    assert (
        sensor.sensor_type
        == "temperature"
    )


    assert (
        sensor.unit
        == "celsius"
    )


    assert (
        sensor.temperature_range
        == (-20, 120)
    )


    assert (
        sensor.status
        == "inactive"
    )



def test_thermal_sensor_activation():

    sensor = create_thermal_sensor()


    sensor.activate()


    assert (
        sensor.status
        == "active"
    )



def test_temperature_measurement():

    sensor = create_thermal_sensor()


    sensor.activate()


    reading = sensor.measure_temperature(
        36.8
    )


    assert (
        reading["sensor_id"]
        == "THERM-001"
    )


    assert (
        reading["temperature"]
        == 36.8
    )


    assert (
        reading["unit"]
        == "celsius"
    )



def test_temperature_range_validation():

    sensor = create_thermal_sensor()


    sensor.activate()


    try:

        sensor.measure_temperature(
            200
        )

        assert False


    except ValueError:

        assert True



def test_temperature_history():

    sensor = create_thermal_sensor()


    sensor.activate()


    sensor.measure_temperature(
        36.5
    )


    sensor.measure_temperature(
        37.0
    )


    assert (
        len(sensor.measurements)
        == 2
    )


    assert (
        sensor.last_value
        == 37.0
    )



def test_thermal_sensor_state():

    sensor = create_thermal_sensor()


    sensor.activate()


    sensor.measure_temperature(
        37.2
    )


    state = (
        sensor.get_thermal_state()
    )


    assert (
        state["sensor_id"]
        == "THERM-001"
    )


    assert (
        state["resolution"]
        == 0.1
    )


    assert (
        state["measurements_count"]
        == 1
    )


    assert (
        state["last_value"]
        == 37.2
    )