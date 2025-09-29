from dotenv import load_dotenv
import os
from os import path, sep, pardir

# Load environment variables from a custom path
load_dotenv(dotenv_path='./env')  # Adjust the path if needed

class Config:
    # Flask secret key
    SECRET_KEY = os.getenv('MY_SECRET_KEY', 'default_secret_key')
    # Base directory
    BASE_DIR = path.abspath(path.dirname(__file__) + sep + pardir)
    # Templates
    TEMPLATES_FOLDER = path.join(BASE_DIR, 'src', 'templates')
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', f"sqlite:///{path.join(BASE_DIR, 'db.sqlite')}"
    )