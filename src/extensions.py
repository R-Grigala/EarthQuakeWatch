from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from flask_migrate import Migrate


from src.config import Config

db = SQLAlchemy()
migrate = Migrate()

api = Api(
    title='Earthquakes API',
    version='1.0',
    description='Earthquakes Data API',
    authorizations=Config.AUTHORIZATION,
    doc='/api'
)