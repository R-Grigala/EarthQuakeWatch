import pymysql
import pytest
import os
from dotenv import load_dotenv

load_dotenv('../../.env')

# You can load these from environment variables or .env file
HOST = os.getenv("AWS_MYSQL_HOST", "amazonaws.com")
USER = os.getenv("AWS_MYSQL_USER", "mysql_user")
PASSWORD = os.getenv("AWS_MYSQL_PASSWORD", "mysql_user_pass")
DATABASE = os.getenv("AWS_MYSQL_DATABASE", "earthquake_db")

def test_mysql_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            connect_timeout=5
        )

        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        assert result[0] == 1  # if connection works, result should be 1

    except Exception as e:
        pytest.fail(f"MySQL connection failed: {e}")

    finally:
        if connection:
            connection.close()
