"""
Tests for KALATRACE Robotics Sensor Fusion
"""


from skills.robotics.perception.sensor_fusion import SensorFusion



class MockSensor:

    def __init__(
        self,
        sensor_id
    ):
        self.sensor_id = sensor_id



def test_register_sensor():

    fusion = SensorFusion()

    sensor = MockSensor(
        "CAMERA-001"
    )

    fusion.register_sensor(
        sensor
    )

    assert (
        "CAMERA-001"
        in fusion.sensors
    )



def test_update_reading():

    fusion = SensorFusion()

    sensor = MockSensor(
        "LIDAR-001"
    )

    fusion.register_sensor(
        sensor
    )


    fusion.update_reading(
        "LIDAR-001",
        {
            "distance": 5.2
        }
    )


    assert (
        fusion.latest_readings["LIDAR-001"]["distance"]
        == 5.2
    )



def test_fuse():

    fusion = SensorFusion()

    sensor = MockSensor(
        "CAMERA-001"
    )

    fusion.register_sensor(
        sensor
    )


    fusion.update_reading(
        "CAMERA-001",
        {
            "object": "person"
        }
    )


    result = fusion.fuse()


    assert result["sensor_count"] == 1

    assert (
        result["readings"]["CAMERA-001"]["object"]
        == "person"
    )



def test_build_observation():

    fusion = SensorFusion()

    sensor = MockSensor(
        "IMU-001"
    )

    fusion.register_sensor(
        sensor
    )


    fusion.update_reading(
        "IMU-001",
        {
            "orientation": "north"
        }
    )


    fusion.fuse()


    observation = (
        fusion.build_observation()
    )


    assert (
        observation["type"]
        == "sensor_fusion"
    )


def test_clear():

    fusion = SensorFusion()

    fusion.latest_readings = {
        "sensor": "data"
    }

    fusion.last_fusion = {
        "test": True
    }


    fusion.clear()


    assert fusion.latest_readings == {}

    assert fusion.last_fusion is None

    assert fusion.fusion_history == []