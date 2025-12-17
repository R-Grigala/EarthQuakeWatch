import pymysql
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv('.env')

# Database parameters
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "event_data")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootPassword")
TABLE_NAME = os.getenv("MYSQL_TABLE", "test_earthquakes")

# API environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
API_KEY = os.getenv("API_KEY", "Z0PTBUfp6K5GsIQqQabKN4WxshnfbGy0")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

def connect_db():
    """
    Establish connection to MySQL database
    Returns connection object if successful, raises exception otherwise
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
        logging.info("Database connection successful.")
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Database connection failed: {e}")
        raise  # Re-raise exception to stop program execution

def fetch_new_events():
    """
    Fetch seismic events edited within the last 1 hour
    Returns list of dictionaries containing event data
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    MIN_MAGNITUDE = 2.5

    SQL_QUERY = f"""
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
        WHERE last_edit_time >= %s AND ml > %s;
    """

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(SQL_QUERY, (one_hour_ago, MIN_MAGNITUDE))
            results = cursor.fetchall()
            logging.info(f"Found {len(results)} new events since {one_hour_ago}")
            return results
    finally:
        conn.close()
    
def post_event_to_api(new_events):
    """
    Send multiple seismic events to the API endpoint
    Iterates through events and tracks success/failure count
    """
    url = f"{API_BASE_URL.rstrip('/')}/api/events"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    }

    sent, failed = 0, 0

    for event in new_events:
        # Build payload from event data

        event_id = event.get("event_id")

        lat = event.get("latitude")
        lon = event.get("longitude")
        
        # Skip if any of the required fields is None
        if lat is None or lon is None :
            failed += 1
            logging.warning(
                f"Skipping event {event_id} due to missing coordinates: "
                f"lat={lat}, lon={lon}"
            )
            continue
            
        payload = {
            "event_id": event["event_id"],
            "seiscomp_oid": event.get("seiscomp_oid"),
            "origin_time": event["origin_time"].isoformat() if event.get("origin_time") else None,
            "origin_msec": event.get("origin_msec"),
            "latitude": lat,
            "longitude": lon,
            "depth": event.get("depth"),
            "region_ge": event.get("region_ge"),
            "region_en": event.get("region_en"),
            "area": event.get("area"),
            "ml": event.get("ml")
        }

        if send_event(url, payload, headers):
            sent += 1
        else:
            failed += 1

    logging.info(f"Finished sending events. sent={sent}, failed={failed}")

def send_event(url, payload, headers):
    """
    Send a single event to the API
    Returns True if successful, False otherwise
    Handles retries and various HTTP status codes
    """
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=API_TIMEOUT)

        logging.info(
            "POST %s -> status=%s, body=%s",
            url, resp.status_code, resp.text
        )

        # Success (create or update)
        if resp.status_code in (200, 201):
            logging.info(f"POST OK id={payload.get('event_id')}")
            return True

        # Treat duplicate as success to be idempotent (if API returns such message)
        if resp.status_code == 400 and "already exists" in (resp.text or "").lower():
            logging.info(f"Duplicate (skip) id={payload.get('event_id')}")
            return True

        # 5xx → server problem
        if resp.status_code >= 500:
            logging.warning(f"Server error {resp.status_code}: {resp.text}")
            return False

        # 4xx (non-duplicate): client-side problem
        logging.error(f"POST failed {resp.status_code}: {resp.text}")
        return False

    except requests.RequestException as e:
        logging.warning("POST exception: %s", e)
        return False

def main():
    # Fetch new events from database
    new_events = fetch_new_events()
    # print(new_events)
    if not new_events:
        # print("No new events to send.")
        logging.info("No new events to send.")  
    else:
        # Send events to API
        post_event_to_api(new_events)
        print(f"Sent {len(new_events)} events.")

if __name__ == "__main__":
    main()