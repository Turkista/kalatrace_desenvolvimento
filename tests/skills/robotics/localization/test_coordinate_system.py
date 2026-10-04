"""
KALATRACE Robotics Coordinate System Tests

Tests the coordinate system model.
"""


from skills.robotics.localization.coordinate_system import CoordinateSystem



def test_coordinate_system_creation():
    """
    Test coordinate system creation.
    """

    system = CoordinateSystem(
        system_name="Cartesian",
        dimensions=3,
        units="meters",
        handedness="right"
    )


    assert system.system_name == "Cartesian"

    assert system.dimensions == 3

    assert system.units == "meters"

    assert system.handedness == "right"



def test_coordinate_system_default_values():
    """
    Test default coordinate system values.
    """

    system = CoordinateSystem(
        system_name="Local"
    )


    assert system.system_name == "Local"

    assert system.dimensions == 3

    assert system.units == "meters"

    assert system.handedness == "right"



def test_coordinate_system_dimensions():
    """
    Test dimension identification.
    """

    system_2d = CoordinateSystem(
        system_name="Plane",
        dimensions=2
    )


    system_3d = CoordinateSystem(
        system_name="Space",
        dimensions=3
    )


    assert system_2d.is_2d()

    assert not system_2d.is_3d()


    assert system_3d.is_3d()

    assert not system_3d.is_2d()



def test_coordinate_system_to_dict():
    """
    Test coordinate system export.
    """

    system = CoordinateSystem(
        system_name="GPS",
        dimensions=3,
        units="degrees"
    )


    data = system.to_dict()


    assert data["system_name"] == "GPS"

    assert data["dimensions"] == 3

    assert data["units"] == "degrees"



def test_coordinate_system_copy():
    """
    Test independent copy.
    """

    system = CoordinateSystem(
        system_name="Robot"
    )


    copied = system.copy()


    assert copied.system_name == "Robot"

    assert copied is not system