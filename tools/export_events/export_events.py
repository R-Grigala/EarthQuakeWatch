import pymysql
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime, timezone, timedelta

# Load environment variables from .env file
load_dotenv('.env')

# MySQL configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "event_data")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootPassword")
TABLE_NAME = os.getenv("MYSQL_TABLE", "test_earthquakes")

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
API_KEY = os.getenv("API_KEY", "Z0PTBUfp6K5GsIQqQabKN4WxshnfbGy0")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))


def connect_db():
    """
    Create and return a MySQL database connection.
    Raises an exception if the connection fails.
    """
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Database connection established")
        return connection
    except pymysql.MySQLError as e:
        logging.error("Database connection failed: %s", e)
        raise


def fetch_new_events():
    """
    Fetch seismic events updated within the last 7 days
    and above the minimum magnitude threshold.
    Returns a list of event dictionaries.
    """
    since_time = datetime.now(timezone.utc) - timedelta(days=7)
    MIN_MAGNITUDE = 2.5

    sql = f"""
        SELECT 
            id AS event_id,
            seiscomp_parent_oid AS seiscomp_oid,
            origin_time,
            origin_msec,
            latitude,
            longitude,
            depth,
            region_ge,
            region_en,
            area,
            ml
        FROM {TABLE_NAME}
        WHERE last_edit_time >= %s
          AND ml > %s;
    """

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (since_time, MIN_MAGNITUDE))
            results = cursor.fetchall()
            logging.info(
                "Fetched %d events updated since %s",
                len(results), since_time
            )
            return results
    finally:
        conn.close()


def post_event_to_api(events):
    """
    Send a list of seismic events to the REST API.
    Tracks successful and failed transmissions.
    """
    url = f"{API_BASE_URL.rstrip('/')}/api/events"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    }

    sent, failed = 0, 0

    for event in events:
        event_id = event.get("event_id")
        lat = event.get("latitude")
        lon = event.get("longitude")

        # Skip events without coordinates
        if lat is None or lon is None:
            failed += 1
            logging.warning(
                "Skipping event %s due to missing coordinates (lat=%s, lon=%s)",
                event_id, lat, lon
            )
            continue

        # Build API payload
        payload = {
            "event_id": event_id,
            "seiscomp_oid": event.get("seiscomp_oid"),
            "origin_time": event["origin_time"].isoformat()
            if event.get("origin_time") else None,
            "origin_msec": event.get("origin_msec"),
            "latitude": lat,
            "longitude": lon,
            "depth": event.get("depth"),
            "region_ge": event.get("region_ge"),
            "region_en": event.get("region_en"),
            "area": event.get("area"),
            "ml": event.get("ml"),
        }

        if send_event(url, payload, headers):
            sent += 1
        else:
            failed += 1

    logging.info("Event sending completed: sent=%d, failed=%d", sent, failed)


def send_event(url, payload, headers):
    """
    Send a single seismic event to the API.
    Returns True on success, False on failure.
    """
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=API_TIMEOUT
        )

        logging.info(
            "POST %s | status=%s | response=%s",
            url, response.status_code, response.text
        )

        # Success: created or updated
        if response.status_code in (200, 201):
            return True

        # Idempotent handling for duplicates
        if response.status_code == 400 and "already exists" in response.text.lower():
            logging.info("Duplicate event ignored (id=%s)", payload.get("event_id"))
            return True

        # Server-side error
        if response.status_code >= 500:
            logging.warning("Server error %s", response.status_code)
            return False

        # Client-side error
        logging.error("Request failed %s: %s", response.status_code, response.text)
        return False

    except requests.RequestException as e:
        logging.warning("Request exception: %s", e)
        return False


def main():
    """
    Main execution flow:
    1. Fetch updated events from MySQL
    2. Send them to the REST API
    """
    events = fetch_new_events()

    if not events:
        logging.info("No new events to send")
        return

    post_event_to_api(events)
    print(f"Processed {len(events)} events")


if __name__ == "__main__":
    main()