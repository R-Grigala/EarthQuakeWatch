import os
import csv
import logging
from dotenv import load_dotenv
import pymysql

# Load environment variables from .env file
load_dotenv(".env")

# Configure file-based logging
LOG_FILENAME = "logs/import_csv_to_mysql.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# MySQL connection settings
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "event_data")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "rootPassword")
TABLE_NAME = os.getenv("MYSQL_TABLE", "test_earthquakes")

# CSV import settings
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Absolute path to CSV file (located near the script)
CSV_PATH = os.path.join(SCRIPT_DIR, "test_v_earthquakes.csv").strip()
CSV_DELIMITER = os.getenv("CSV_DELIMITER", ",")
CSV_ENCLOSED_BY = os.getenv("CSV_ENCLOSED_BY", '"')
CSV_IGNORE_HEADER = int(os.getenv("CSV_IGNORE_HEADER", "1"))

# Force Python-based insert (not used here, reserved for fallback logic)
FORCE_PY_INSERT = os.getenv("FORCE_PY_INSERT", "0") == "1"

print(CSV_PATH)

# Line terminators to try (Linux and Windows compatibility)
LINE_TERMINATORS_TO_TRY = ["\n", "\r\n"]


def connect(local_infile: bool):
    """
    Create a MySQL connection.
    local_infile=True is required for LOAD DATA LOCAL INFILE.
    """
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset="utf8mb4",
        autocommit=False,
        local_infile=local_infile,
    )


def import_data():
    """
    Import CSV data into MySQL using LOAD DATA LOCAL INFILE.
    Automatically retries with different line terminators.
    """
    if not CSV_PATH:
        raise ValueError("CSV_PATH is empty. Set CSV_PATH in .env")

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    conn = connect(local_infile=True)
    try:
        with conn.cursor() as cur:
            last_err = None

            # Try different line terminators to avoid platform-specific issues
            for lt in LINE_TERMINATORS_TO_TRY:
                try:
                    sql = f"""
                        LOAD DATA LOCAL INFILE %s
                        INTO TABLE `{TABLE_NAME}`
                        FIELDS TERMINATED BY %s
                        ENCLOSED BY %s
                        LINES TERMINATED BY %s
                        {"IGNORE " + str(CSV_IGNORE_HEADER) + " LINES" if CSV_IGNORE_HEADER else ""}
                    """
                    cur.execute(sql, (CSV_PATH, CSV_DELIMITER, CSV_ENCLOSED_BY, lt))
                    conn.commit()

                    logging.info(
                        "CSV import succeeded using line terminator %r",
                        lt
                    )
                    return

                except Exception as e:
                    conn.rollback()
                    last_err = e
                    logging.warning(
                        "CSV import failed with line terminator %r: %s",
                        lt, e
                    )

            # Raise the last error if all attempts fail
            raise last_err if last_err else RuntimeError(
                "CSV import failed for unknown reasons"
            )

    finally:
        conn.close()


def main():
    """
    Entry point:
    Executes CSV import into MySQL table.
    """
    try:
        import_data()
        logging.info("CSV import completed successfully.")
    except Exception as e:
        logging.warning("CSV import failed: %s", e)


if __name__ == "__main__":
    main()