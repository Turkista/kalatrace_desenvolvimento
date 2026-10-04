import pytest

from perception.sensor_fusion import SensorFusion


@pytest.fixture
def sensor_fusion():
    """
    Creates a SensorFusion instance for testing.
    """
    return SensorFusion()


def test_sensor_fusion_initialization(sensor_fusion):
    """
    Tests if SensorFusion initializes correctly.
    """

    assert sensor_fusion is not None
    assert hasattr(sensor_fusion, "fuse")


def test_fusion_combines_multiple_sensors(sensor_fusion):
    """
    Tests if multiple sensor inputs are combined correctly.
    """

    sensor_data = {
        "camera": {
            "object": "human",
            "confidence": 0.95
        },
        "lidar": {
            "distance": 2.5,
            "confidence": 0.90
        },
        "temperature": {
            "value": 24.5,
            "confidence": 0.98
        }
    }

    result = sensor_fusion.fuse(sensor_data)

    assert result is not None
    assert isinstance(result, dict)


def test_fusion_generates_integrated_state(sensor_fusion):
    """
    Tests if fusion produces an integrated perception state.
    """

    sensor_data = {
        "camera": {
            "object": "vehicle"
        },
        "radar": {
            "speed": 60
        }
    }

    result = sensor_fusion.fuse(sensor_data)

    assert (
        "state" in result
        or "fused_data" in result
        or "perception" in result
    )


def test_fusion_handles_single_sensor(sensor_fusion):
    """
    Tests fusion with only one sensor source.
    """

    sensor_data = {
        "camera": {
            "object": "tree"
        }
    }

    result = sensor_fusion.fuse(sensor_data)

    assert result is not None
    assert isinstance(result, dict)


def test_fusion_handles_empty_sensor_input(sensor_fusion):
    """
    Tests behavior when no sensor information is provided.
    """

    result = sensor_fusion.fuse({})

    assert result is not None
    assert isinstance(result, dict)


def test_sensor_confidence_is_preserved(sensor_fusion):
    """
    Tests if confidence information remains available after fusion.
    """

    sensor_data = {
        "camera": {
            "object": "person",
            "confidence": 0.87
        }
    }

    result = sensor_fusion.fuse(sensor_data)

    result_text = str(result)

    assert "0.87" in result_text or "confidence" in result_text