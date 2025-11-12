
import pymysql
import os
from dotenv import load_dotenv
import logging

# გარემოს ცვლადების ჩატვირთვა
load_dotenv('../../.env')

# logging-ის კონფიგურაცია
log_filename = "export_csv_from_db.log"
logging.basicConfig(filename=log_filename , level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# მონაცემთა ბაზის პარამეტრები
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD_STR')

# გარემოს ცვლადების შემოწმება
if not all([MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD]):
    raise ValueError("მონაცემთა ბაზის პარამეტრები დაკარგულია!")