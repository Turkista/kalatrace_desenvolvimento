"""
KALATRACE Robotics Perception Integration Test

Validates the complete perception cycle.
"""


from skills.robotics.perception.observation import (
    Observation
)

from skills.robotics.perception.sensor_fusion import (
    SensorFusion
)

from skills.robotics.perception.object_tracker import (
    ObjectTracker
)

from skills.robotics.perception.environment_model import (
    EnvironmentModel
)

from skills.robotics.perception.perception_pipeline import (
    PerceptionPipeline
)



class MockSensor:

    def __init__(
        self,
        sensor_id
    ):

        self.sensor_id = sensor_id



class IntegrationPerceptionManager:

    def __init__(self):

        self.observations = []


    def add_observation(
        self,
        observation
    ):

        self.observations.append(
            observation
        )


    def get_observations(self):

        return self.observations



def create_perception_system():

    perception_manager = (
        IntegrationPerceptionManager()
    )


    sensor_fusion = SensorFusion()


    object_tracker = ObjectTracker()


    environment_model = EnvironmentModel()



    pipeline = PerceptionPipeline(

        perception_manager,

        sensor_fusion,

        object_tracker,

        environment_model
    )


    return (

        perception_manager,

        sensor_fusion,

        object_tracker,

        environment_model,

        pipeline
    )



def test_complete_perception_cycle():

    (
        perception_manager,
        sensor_fusion,
        object_tracker,
        environment_model,
        pipeline

    ) = create_perception_system()



    # ---------------------------
    # 1. Create sensors
    # ---------------------------

    camera = MockSensor(
        "camera_01"
    )


    lidar = MockSensor(
        "lidar_01"
    )


    sensor_fusion.register_sensor(
        camera
    )

    sensor_fusion.register_sensor(
        lidar
    )



    # ---------------------------
    # 2. Generate observations
    # ---------------------------

    observation = Observation(

        observation_id="OBS-001",

        robot_id="ROBOT-001",

        sensor_id="camera_01",

        observation_type="object_detection",

        value="person",

        unit="classification",

        confidence=0.95
    )


    perception_manager.add_observation(
        observation.to_dict()
    )



    # ---------------------------
    # 3. Update sensor readings
    # ---------------------------

    sensor_fusion.update_reading(

        "camera_01",

        {
            "object": "person",
            "confidence": 0.95
        }
    )


    sensor_fusion.update_reading(

        "lidar_01",

        {
            "distance": 5.2
        }
    )



    # ---------------------------
    # 4. Track object
    # ---------------------------

    object_tracker.register_object(

        "OBJ-001",

        {
            "type": "person",
            "position": [10, 5]
        }
    )



    # ---------------------------
    # 5. Update environment
    # ---------------------------

    environment_model.update_robot_state(

        {
            "position": [0, 0],
            "battery": 90
        }
    )


    environment_model.add_object(

        "OBJ-001",

        {
            "type": "person",
            "position": [10, 5]
        }
    )



    # ---------------------------
    # 6. Execute perception cycle
    # ---------------------------

    snapshot = pipeline.process()



    # ---------------------------
    # Assertions
    # ---------------------------

    assert len(
        snapshot["observations"]
    ) == 1



    assert (
        snapshot["fusion"]["sensor_count"]
        == 2
    )



    assert (
        "OBJ-001"
        in snapshot["tracked_objects"]
    )



    assert (
        snapshot["environment"]["object_count"]
        == 1
    )



def test_perception_state_persistence():

    (
        perception_manager,
        sensor_fusion,
        object_tracker,
        environment_model,
        pipeline

    ) = create_perception_system()



    object_tracker.register_object(

        "OBJ-002",

        {
            "type": "vehicle"
        }
    )


    environment_model.add_object(

        "OBJ-002",

        {
            "type": "vehicle"
        }
    )



    exported = pipeline.export()



    assert (
        "OBJ-002"
        in exported["tracked_objects"]
    )


    assert (
        exported["environment"]["object_count"]
        == 1
    )



def test_perception_clear_cycle():

    (
        perception_manager,
        sensor_fusion,
        object_tracker,
        environment_model,
        pipeline

    ) = create_perception_system()



    object_tracker.register_object(

        "OBJ-003",

        {}
    )


    environment_model.add_object(

        "OBJ-003",

        {}
    )


    pipeline.clear()



    assert (
        object_tracker.object_count()
        == 0
    )


    assert (
        environment_model.object_count()
        == 0
    )