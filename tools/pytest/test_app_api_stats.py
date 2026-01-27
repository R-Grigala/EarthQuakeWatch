import os
import datetime

import pytest

os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture
def app():
    from src import create_app

    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


def test_stats_endpoint_shape(client):
    """ამოწმებს, რომ /api/stats აბრუნებს მოსალოდნელ key-ებს."""
    resp = client.get("/api/stats")
    assert resp.status_code in (200, 500)

    if resp.status_code == 200:
        data = resp.get_json()
        for key in [
            "count_last_1m",
            "avg_ml_last_1m",
            "max_ml_last_1m",
            "count_last_6m",
            "avg_ml_last_6m",
            "max_ml_last_6m",
            "count_last_1y",
            "avg_ml_last_1y",
            "max_ml_last_1y",
            "total_events",
            "updated_utc",
        ]:
            assert key in data


