import pytest
from src.config import Config


# ==========================
# Smoke test for GET /api/events
# ==========================
def test_get_events_empty_db(client):
    """
    GET /api/events:
    - ახალ ტესტურ ბაზაზე, სადაც შეიძლება არ იყოს ჩანაწერები, ველოდებით 200 ან 404-ს.
    - სხეულის სტრუქტურას ზედმეტად არ ვამოწმებთ, მთავარია სწორი JSON და სტატუსი.
    """
    resp = client.get("/api/events")
    assert resp.status_code == 200
    data = resp.get_json()

    # უბრალოდ ვამოწმებთ, რომ JSON მივიღეთ (dict ან list)
    assert isinstance(data, (dict, list))


# ==========================
# POST + GET roundtrip test
# ==========================
def test_post_and_get_event(client):
    """POST /api/events with correct API key, then GET."""
    event_payload = {
        "event_id": 123,  # parser ითხოვს Integer-ს
        "seiscomp_oid": "OID001",
        "origin_time": "2026-01-28T12:00:00",
        "origin_msec": 0,
        "latitude": 41.7,
        "longitude": 44.8,
        "depth": 10.0,
        "region_ge": "Region GE",
        "region_en": "Region EN",
        "area": "Some Area",
        "ml": 4.5,
    }

    headers = {"X-API-Key": Config.API_KEY}

    # --- POST new event ---
    post_resp = client.post("/api/events", json=event_payload, headers=headers)
    assert post_resp.status_code in (200, 201)
    post_data = post_resp.get_json()
    assert "created successfully" in post_data.get("message", "")

    # --- GET events ---
    get_resp = client.get("/api/events")
    assert get_resp.status_code == 200
    get_data = get_resp.get_json()
    assert any(e.get("event_id") == 123 for e in get_data)


# ==========================
# POST with invalid API key
# ==========================
def test_post_unauthorized(client):
    event_payload = {
        "event_id": 124,
        "origin_time": "2026-01-28T12:00:00",
        "latitude": 41.7,
        "longitude": 44.8,
        "depth": 10.0,
        "ml": 3.0,
    }
    headers = {"X-API-Key": "WRONG_KEY"}
    resp = client.post("/api/events", json=event_payload, headers=headers)
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Unauthorized" in data.get("error", "")
