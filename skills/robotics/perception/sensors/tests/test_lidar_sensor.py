"""
KALATRACE Robotics LiDAR Sensor Tests

Validates the spatial perception sensor.

Tests:

- LiDAR sensor creation
- Sensor activation
- Distance measurement
- Distance validation
- Environment scanning
- LiDAR state reporting
"""


from skills.robotics.perception.sensors.lidar_sensor import (
    LidarSensor
)



def create_lidar_sensor():

    sensor = LidarSensor(

        sensor_id="LIDAR-001",

        range_limit=50,

        accuracy=0.99,

        scan_rate=20,

        manufacturer="KALATRACE Spatial"
    )

    return sensor



def test_lidar_sensor_creation():

    sensor = create_lidar_sensor()


    assert (
        sensor.sensor_id
        == "LIDAR-001"
    )


    assert (
        sensor.sensor_type
        == "distance"
    )


    assert (
        sensor.unit
        == "meters"
    )


    assert (
        sensor.range_limit
        == 50
    )


    assert (
        sensor.status
        == "inactive"
    )



def test_lidar_activation():

    sensor = create_lidar_sensor()


    sensor.activate()


    assert (
        sensor.status
        == "active"
    )



def test_distance_measurement():

    sensor = create_lidar_sensor()


    sensor.activate()


    measurement = sensor.measure_distance(
        3.5
    )


    assert (
        measurement["distance"]
        == 3.5
    )


    assert (
        measurement["unit"]
        == "meters"
    )


    assert (
        sensor.last_value
        == 3.5
    )



def test_negative_distance_validation():

    sensor = create_lidar_sensor()


    sensor.activate()


    try:

        sensor.measure_distance(
            -1
        )

        assert False


    except ValueError:

        assert True



def test_distance_range_validation():

    sensor = create_lidar_sensor()


    sensor.activate()


    try:

        sensor.measure_distance(
            100
        )

        assert False


    except ValueError:

        assert True



def test_environment_scan():

    sensor = create_lidar_sensor()


    sensor.activate()


    scan = sensor.scan_environment(

        [
            2.5,
            5.0,
            10.0
        ]

    )


    assert (
        len(scan)
        == 3
    )


    assert (
        scan[0]["distance"]
        == 2.5
    )


    assert (
        scan[2]["distance"]
        == 10.0
    )



def test_lidar_state():

    sensor = create_lidar_sensor()


    sensor.activate()


    sensor.measure_distance(
        4.5
    )


    state = (
        sensor.get_lidar_state()
    )


    assert (
        state["sensor_id"]
        == "LIDAR-001"
    )


    assert (
        state["range_limit"]
        == 50
    )


    assert (
        state["scan_rate"]
        == 20
    )


    assert (
        state["points_detected"]
        == 1
    )