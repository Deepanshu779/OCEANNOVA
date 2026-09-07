def test_backend_imports():
    from app.main import app

    paths = {route.path for route in app.routes}
    assert "/" in paths
    assert "/api/v1/health" in paths
    assert "/api/v1/spills/" in paths
    assert "/api/v1/spills/{spill_id}/investigation" in paths
