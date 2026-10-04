"""
Tests for KALATRACE Robotics Perception Pipeline
"""


from skills.robotics.perception.perception_pipeline import (
    PerceptionPipeline
)



class MockPerceptionManager:
    """
    Mock perception manager.
    """

    def get_observations(self):

        return [
            {
                "id": "OBS-001",
                "type": "object_detection",
                "value": "person"
            }
        ]



class MockSensorFusion:
    """
    Mock sensor fusion.
    """

    def __init__(self):

        self.last_fusion = None


    def validate(self):

        return True


    def fuse(self):

        self.last_fusion = {

            "sensor_count": 2,

            "readings": {

                "camera": "person",

                "lidar": 5.0
            }
        }

        return self.last_fusion


    def get_last_fusion(self):

        return self.last_fusion


    def clear(self):

        self.last_fusion = None



class MockObjectTracker:
    """
    Mock object tracker.
    """

    def __init__(self):

        self.objects = {

            "OBJ-001": {

                "type": "person"
            }
        }


    def list_objects(self):

        return self.objects


    def clear(self):

        self.objects.clear()



class MockEnvironmentModel:
    """
    Mock environment model.
    """

    def export(self):

        return {

            "environment": "indoor",

            "objects": 1
        }


    def clear(self):

        pass



def create_pipeline():

    return PerceptionPipeline(

        MockPerceptionManager(),

        MockSensorFusion(),

        MockObjectTracker(),

        MockEnvironmentModel()
    )



def test_pipeline_process():

    pipeline = create_pipeline()


    result = pipeline.process()


    assert "observations" in result

    assert "fusion" in result

    assert "environment" in result

    assert "tracked_objects" in result


    assert len(
        result["observations"]
    ) == 1


    assert (
        result["fusion"]["sensor_count"]
        == 2
    )


    assert (
        result["tracked_objects"]["OBJ-001"]["type"]
        == "person"
    )



def test_pipeline_get_environment():

    pipeline = create_pipeline()


    environment = pipeline.get_environment()


    assert (
        environment["environment"]
        == "indoor"
    )



def test_pipeline_get_objects():

    pipeline = create_pipeline()


    objects = pipeline.get_objects()


    assert "OBJ-001" in objects



def test_pipeline_export():

    pipeline = create_pipeline()


    pipeline.process()


    exported = pipeline.export()


    assert "observations" in exported

    assert "fusion" in exported

    assert "environment" in exported

    assert "tracked_objects" in exported



def test_pipeline_clear():

    pipeline = create_pipeline()


    pipeline.clear()


    assert (
        pipeline.sensor_fusion.last_fusion
        is None
    )


    assert (
        pipeline.object_tracker.objects
        == {}
    )