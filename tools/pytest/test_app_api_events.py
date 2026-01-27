import os
import datetime

import pytest

os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture
def app():
    """Create a Flask app instance for testing."""
    from src import create_app

    test_app = create_app()
    return test_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


def test_events_get_empty_db_returns_404(client):
    """If no events in DB, /api/events უნდა აბრუნებდეს 404-ს ქართულ მესიჯთან ერთად."""
    resp = client.get("/api/events")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "მიწისძვრები არ მოიძებნა." in (data.get("error") or "")


def test_events_post_without_api_key_is_unauthorized(client):
    """POST /api/events API key-ს გარეშე უნდა იყოს 401."""
    payload = {
        "event_id": 1,
        "origin_time": datetime.datetime.utcnow().isoformat(),
        "latitude": 41.0,
        "longitude": 44.0,
        "depth": 10.0,
        "ml": 3.2,
    }

    resp = client.post("/api/events", json=payload)
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Unauthorized" in (data.get("error") or "")


def test_events_post_and_get_roundtrip(client, monkeypatch):
    """წარმატებით ქმნის event-ს და შემდეგ GET აბრუნებს მას."""
    # დააყენე სწორი API_KEY კონფიგში
    from src import config as config_module

    monkeypatch.setenv("API_KEY", "test-secret")
    # ხელახლა ჩატვირთვა, თუ უკვე იმპორტირებულია
    import importlib

    importlib.reload(config_module)

    from src.config import Config

    headers = {"X-API-Key": Config.API_KEY}

    payload = {
        "event_id": 999,
        "origin_time": datetime.datetime.utcnow().isoformat(),
        "latitude": 41.0,
        "longitude": 44.0,
        "depth": 5.0,
        "ml": 4.5,
    }

    # შექმნა
    resp_post = client.post("/api/events", json=payload, headers=headers)
    assert resp_post.status_code in (200, 201)

    # წამოღება
    resp_get = client.get("/api/events")
    assert resp_get.status_code == 200
    data = resp_get.get_json()
    assert isinstance(data, list)
    assert any(e["event_id"] == 999 for e in data)

