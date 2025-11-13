import pymysql
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime, timezone, timedelta

# გარემოს ცვლადების ჩატვირთვა
load_dotenv('../../.env')

# logging-ის კონფიგურაცია
log_filename = "export_events_from_db.log"
logging.basicConfig(filename=log_filename , level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# მონაცემთა ბაზის პარამეტრები
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "event_data")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootPassword")
TABLE_NAME = os.getenv("MYSQL_TABLE", "test_earthquakes")

# API env
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")
API_KEY = os.getenv("API_KEY", "Z0PTBUfp6K5GsIQqQabKN4WxshnfbGy0")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

def connect_db():
    # მონაცემთა ბაზასთან კავშირის ტესტი
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        logging.info("მონაცემთა ბაზასთან კავშირი წარმატებით შესრულდა.")
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"მონაცემთა ბაზასთან კავშირი ვერ მოხერხდა: {e}")
        raise  # შეცდომის გადაცემა, რომ პროგრამა შეწყდეს

def fetch_new_events():
    """Fetch events edited within the last 1 hour"""
    # one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    one_hour_ago = "2022-02-12 15:18:03.338792+00:00"


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
            area
        FROM {TABLE_NAME}
        WHERE last_edit_time >= %s;
    """

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(SQL_QUERY, (one_hour_ago,))
            results = cursor.fetchall()
            logging.info(f"Found {len(results)} new events since {one_hour_ago}")
            return results

    finally:
        conn.close()
    
def post_event_to_api(new_events):
    url = f"{API_BASE_URL.rstrip('/')}/api/events"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    }

    sent, failed = 0, 0

    for event in new_events:
        payload = {
            "event_id": event["event_id"],
            "seiscomp_oid": event.get("seiscomp_oid"),
            "origin_time": event.get("origin_time_iso"),
            "origin_msec": event.get("origin_msec"),
            "latitude": event.get("latitude"),
            "longitude": event.get("longitude"),
            "depth": event.get("depth"),
            "region_ge": event.get("region_ge"),
            "region_en": event.get("region_en"),
            "area": event.get("area"),
        }

        if send_event(url, payload, headers):
            sent += 1
        else:
            failed += 1

    logging.info(f"Finished sending events. sent={sent}, failed={failed}")

def send_event(url, payload, headers):
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=API_TIMEOUT)

        logging.info(
            "POST %s -> status=%s, body=%s",
            url, resp.status_code, resp.text
        )

        # success (create or update)
        if resp.status_code in (200, 201):
            logging.info(f"POST OK id={payload.get('event_id')}")
            return True

        # treat duplicate as success to be idempotent (if your API returns such message)
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


if __name__ == "__main__":
    new_events = fetch_new_events()
    if not new_events:
        print("No new events to send.")
        logging.info("No new events to send.")
    else:
        post_event_to_api(new_events)
        print(f"Sent {len(new_events)} events.")