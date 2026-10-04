"""
KALATRACE Robot Agent Tests

Validates the robotic entity model
inside the KALATRACE ecosystem.

Tests:

- Robot identity
- Capabilities
- Sensors
- Actuators
- Connection state
- Missions
- Profile generation
"""


from skills.robotics.robot_agent import RobotAgent



def create_robot():

    robot = RobotAgent(
        robot_id="LAB-001",
        model="Research Robot",
        manufacturer="KALATRACE Robotics"
    )

    return robot



def test_robot_creation():

    robot = create_robot()


    assert robot.robot_id == "LAB-001"

    assert robot.model == "Research Robot"

    assert (
        robot.manufacturer
        == "KALATRACE Robotics"
    )


    assert robot.status == "offline"



def test_robot_capabilities():

    robot = create_robot()


    robot.add_capability(
        "computer_vision"
    )

    robot.add_capability(
        "sample_analysis"
    )


    assert (
        "computer_vision"
        in robot.capabilities
    )


    assert (
        "sample_analysis"
        in robot.capabilities
    )



def test_robot_sensors():

    robot = create_robot()


    robot.add_sensor(
        "camera"
    )


    robot.add_sensor(
        "temperature_sensor"
    )


    assert (
        "camera"
        in robot.sensors
    )


    assert (
        "temperature_sensor"
        in robot.sensors
    )



def test_robot_actuators():

    robot = create_robot()


    robot.add_actuator(
        "robotic_arm"
    )


    robot.add_actuator(
        "gripper"
    )


    assert (
        "robotic_arm"
        in robot.actuators
    )


    assert (
        "gripper"
        in robot.actuators
    )



def test_robot_connection_state():

    robot = create_robot()


    robot.connect()


    assert (
        robot.status
        == "connected"
    )


    robot.disconnect()


    assert (
        robot.status
        == "offline"
    )



def test_robot_mission():

    robot = create_robot()


    robot.connect()


    robot.assign_mission(
        "Sample Analysis"
    )


    assert (
        robot.current_mission
        == "Sample Analysis"
    )


    assert (
        robot.status
        == "executing"
    )



def test_robot_profile():

    robot = create_robot()


    robot.add_capability(
        "vision"
    )


    robot.add_sensor(
        "camera"
    )


    robot.add_actuator(
        "arm"
    )


    profile = robot.get_profile()


    assert (
        profile["robot_id"]
        == "LAB-001"
    )


    assert (
        "vision"
        in profile["capabilities"]
    )


    assert (
        "camera"
        in profile["sensors"]
    )


    assert (
        "arm"
        in profile["actuators"]
    )