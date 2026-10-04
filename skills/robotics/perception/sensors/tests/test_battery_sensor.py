"""
KALATRACE Robotics Battery Sensor Tests

Validates the internal state perception sensor.

Tests:

- Battery sensor creation
- Sensor activation
- Battery measurement
- Battery range validation
- Low battery detection
- Energy history
- Battery state reporting
"""


from skills.robotics.perception.sensors.battery_sensor import (
    BatterySensor
)



def create_battery_sensor():

    sensor = BatterySensor(

        sensor_id="BAT-001",

        battery_capacity=5000,

        accuracy=0.99,

        manufacturer="KALATRACE Energy"
    )

    return sensor



def test_battery_sensor_creation():

    sensor = create_battery_sensor()


    assert (
        sensor.sensor_id
        == "BAT-001"
    )


    assert (
        sensor.sensor_type
        == "battery"
    )


    assert (
        sensor.unit
        == "percentage"
    )


    assert (
        sensor.battery_capacity
        == 5000
    )


    assert (
        sensor.status
        == "inactive"
    )



def test_battery_sensor_activation():

    sensor = create_battery_sensor()


    sensor.activate()


    assert (
        sensor.status
        == "active"
    )



def test_battery_measurement():

    sensor = create_battery_sensor()


    sensor.activate()


    reading = sensor.measure_battery(
        85
    )


    assert (
        reading["battery"]
        == 85
    )


    assert (
        reading["unit"]
        == "percentage"
    )


    assert (
        reading["capacity"]
        == 5000
    )


    assert (
        sensor.last_value
        == 85
    )



def test_battery_range_validation():

    sensor = create_battery_sensor()


    sensor.activate()


    try:

        sensor.measure_battery(
            150
        )

        assert False


    except ValueError:

        assert True



def test_low_battery_detection():

    sensor = create_battery_sensor()


    sensor.activate()


    sensor.measure_battery(
        15
    )


    assert (
        sensor.is_low_battery()
        is True
    )



def test_energy_history():

    sensor = create_battery_sensor()


    sensor.activate()


    sensor.measure_battery(
        90
    )


    sensor.measure_battery(
        80
    )


    assert (
        len(sensor.energy_history)
        == 2
    )


    assert (
        sensor.energy_history[1]["battery"]
        == 80
    )



def test_battery_state():

    sensor = create_battery_sensor()


    sensor.activate()


    sensor.measure_battery(
        70
    )


    state = (
        sensor.get_battery_state()
    )


    assert (
        state["sensor_id"]
        == "BAT-001"
    )


    assert (
        state["battery_capacity"]
        == 5000
    )


    assert (
        state["measurements"]
        == 1
    )


    assert (
        state["low_battery"]
        is False
    )


    assert (
        state["last_value"]
        == 70
    )