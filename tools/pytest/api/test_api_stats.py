import pytest
from datetime import datetime, timezone

def test_stats_endpoint_empty_db(client):
    """Test GET /api/stats with empty DB"""
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.get_json()

    # Ensure all expected keys exist
    expected_keys = [
        "count_last_1m", "avg_ml_last_1m", "max_ml_last_1m",
        "count_last_6m", "avg_ml_last_6m", "max_ml_last_6m",
        "count_last_1y", "avg_ml_last_1y", "max_ml_last_1y",
        "total_events", "updated_utc"
    ]
    for key in expected_keys:
        assert key in data

    # conftest-ში populate_db_core() ერთი event-ს ამატებს:
    # origin_time=2025-08-15, ml=3.5
    #
    # დროის ფანჯრები (დღევანდელი now-სთვის):
    # - 1m: seed event-ს არ ეკუთვნის -> 0
    # - 6m: ეკუთვნის -> 1
    # - 1y: ეკუთვნის -> 1
    assert data["count_last_1m"] == 0
    assert data["count_last_6m"] == 1
    assert data["count_last_1y"] == 1

    # მთლიანად ერთია მოვლენების რაოდენობა
    assert data["total_events"] == 1

    # ML სტატისტიკა: მხოლოდ ერთი მნიშვნელობაა 6m/1y ფანჯრებში -> 3.5
    assert data["avg_ml_last_1m"] == 0.0
    assert data["avg_ml_last_6m"] == 3.5
    assert data["avg_ml_last_1y"] == 3.5
    assert data["max_ml_last_1m"] == 0.0
    assert data["max_ml_last_6m"] == 3.5
    assert data["max_ml_last_1y"] == 3.5

    # updated_utc არ უნდა იყოს None, რადგან ერთი event უკვე არის
    assert data["updated_utc"] is not None


def test_stats_endpoint_with_data(client, app):
    """Test GET /api/stats with some inserted events"""
    from src.models import SeismicEvent
    now = datetime.now(timezone.utc)

    # Insert test events
    events = [
        SeismicEvent(event_id=1, origin_time=now, ml=4.5, latitude=41.7, longitude=44.8, depth=10.0),
        SeismicEvent(event_id=2, origin_time=now, ml=5.2, latitude=41.8, longitude=44.9, depth=12.0),
        SeismicEvent(event_id=3, origin_time=now, ml=3.8, latitude=41.9, longitude=45.0, depth=8.0),
    ]

    with app.app_context():
        for e in events:
            e.create()  # or e.save() depending on your model

    # Call stats endpoint
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.get_json()

    # ერთი seed event + სამი ახალი -> სულ 4
    assert data["total_events"] == 4

    # ბოლო 1 თვე: მხოლოდ სამი ახალი (seed ზედმეტად ძველია 1m ფანჯრისთვის)
    assert data["count_last_1m"] == 3

    # ბოლო 6 თვე / 1 წელი: seed + სამი ახალი -> 4
    assert data["count_last_6m"] == 4
    assert data["count_last_1y"] == 4

    # ტიპები
    assert isinstance(data["avg_ml_last_1m"], float)
    assert isinstance(data["max_ml_last_1m"], float)

    # ახალი ML-ები: [4.5, 5.2, 3.8] -> max = 5.2, median(avg_ml) = 4.5
    assert data["max_ml_last_1m"] == 5.2
    assert data["avg_ml_last_1m"] == 4.5
