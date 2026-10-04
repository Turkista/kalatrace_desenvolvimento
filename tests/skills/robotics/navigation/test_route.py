"""
KALATRACE Robotics Navigation Route Tests

Tests the navigation route model.
"""


from skills.robotics.navigation.route import Route



def test_route_creation():
    """
    Test route creation.
    """

    route = Route(
        route_id="route_001"
    )


    assert route.route_id == "route_001"

    assert route.path_count() == 0

    assert route.destination is None



def test_add_path():
    """
    Test path insertion.
    """

    route = Route(
        route_id="inspection"
    )


    route.add_path(
        {
            "path_id": "path_001"
        }
    )


    assert route.path_count() == 1

    assert (
        route.paths[0]["path_id"]
        == "path_001"
    )



def test_remove_path():
    """
    Test path removal.
    """

    route = Route(
        route_id="remove_test"
    )


    route.add_path(
        {
            "path_id": "path_001"
        }
    )


    route.remove_path(
        0
    )


    assert route.path_count() == 0



def test_update_destination():
    """
    Test destination update.
    """

    route = Route(
        route_id="destination_test"
    )


    route.update_destination(
        {
            "x": 100,
            "y": 200,
            "z": 10
        }
    )


    assert route.destination["x"] == 100

    assert route.destination["z"] == 10



def test_route_export():
    """
    Test route export.
    """

    route = Route(
        route_id="export_test"
    )


    route.add_path(
        {
            "path_id": "main_path"
        }
    )


    data = route.export()


    assert data["route_id"] == "export_test"

    assert data["path_count"] == 1

    assert (
        data["paths"][0]["path_id"]
        == "main_path"
    )



def test_route_clear():
    """
    Test route reset.
    """

    route = Route(
        route_id="clear_test"
    )


    route.add_path(
        {
            "path_id": "temporary"
        }
    )


    route.update_destination(
        {
            "x": 1
        }
    )


    route.clear()


    assert route.path_count() == 0

    assert route.destination is None