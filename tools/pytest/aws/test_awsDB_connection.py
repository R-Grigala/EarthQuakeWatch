import os

import pymysql
import pytest
from dotenv import load_dotenv, find_dotenv

# Load .env from project root (or nearest found)
load_dotenv(find_dotenv(), override=False)

# AWS MySQL connection settings (from environment)
HOST = os.getenv("AWS_MYSQL_HOST", "")
USER = os.getenv("AWS_MYSQL_USER", "")
PASSWORD = os.getenv("AWS_MYSQL_PASSWORD", "")
DATABASE = os.getenv("AWS_MYSQL_DATABASE", "")


@pytest.mark.integration
def test_aws_mysql_connection():
    """
    Simple connectivity check to AWS MySQL (RDS).

    NOTE:
    - ტესტი გაეშვება მხოლოდ მაშინ, თუ AWS_MYSQL_* env ცვლადები რეალურად არის მონიშნული.
    - წინააღმდეგ შემთხვევაში, ტესტი ავტომატურად გაიΧტება (skip), რომ ლოკალურ დეველოპმენტს ხელი არ შეუშალოს.
    """
    if not (HOST and USER and PASSWORD and DATABASE):
        pytest.skip("AWS_MYSQL_* env variables not configured; skipping AWS MySQL connection test")

    try:
        with pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()

        assert result and result[0] == 1

    except Exception as e:
        pytest.fail(f"AWS MySQL connection failed: {e}")
