"""
KALATRACE Robotics Camera Sensor Tests

Validates the robotic vision sensor.

Tests:

- Camera creation
- Camera activation
- Frame capture
- Frame counter
- Camera state
"""


from skills.robotics.perception.sensors.camera_sensor import (
    CameraSensor
)



def create_camera():

    camera = CameraSensor(

        sensor_id="CAM-001",

        resolution="1920x1080",

        frame_rate=30,

        accuracy=0.95,

        manufacturer="KALATRACE Vision"
    )


    return camera



def test_camera_creation():

    camera = create_camera()


    assert (
        camera.sensor_id
        == "CAM-001"
    )


    assert (
        camera.sensor_type
        == "vision"
    )


    assert (
        camera.unit
        == "image"
    )


    assert (
        camera.resolution
        == "1920x1080"
    )


    assert (
        camera.status
        == "inactive"
    )



def test_camera_activation():

    camera = create_camera()


    camera.activate()


    assert (
        camera.status
        == "active"
    )



def test_camera_capture_frame():

    camera = create_camera()


    camera.activate()


    frame = camera.capture_frame(

        "frame_001.jpg"

    )


    assert (
        frame["sensor_id"]
        == "CAM-001"
    )


    assert (
        frame["type"]
        == "image"
    )


    assert (
        frame["data"]
        == "frame_001.jpg"
    )



def test_camera_frame_counter():

    camera = create_camera()


    camera.activate()


    camera.capture_frame(
        "frame_001.jpg"
    )


    camera.capture_frame(
        "frame_002.jpg"
    )


    assert (
        camera.frames_captured
        == 2
    )



def test_camera_state():

    camera = create_camera()


    camera.activate()


    camera.capture_frame(
        "frame_test.jpg"
    )


    state = (
        camera.get_camera_state()
    )


    assert (
        state["sensor_id"]
        == "CAM-001"
    )


    assert (
        state["resolution"]
        == "1920x1080"
    )


    assert (
        state["frame_rate"]
        == 30
    )


    assert (
        state["frames_captured"]
        == 1
    )