from flask import Flask, render_template
# from flask_cors import CORS

from src.config import Config
from src.api import api
from src.commands import init_db, populate_db
from src.extensions import db, api, migrate

COMMANDS = [init_db, populate_db]

def create_app(config=Config):
    app = Flask(__name__)
    # CORS(app)
    app.config.from_object(config)

    @app.route('/')
    def home():
        return render_template('index.html')

    register_extensions(app)
    # register_blueprints(app)
    register_commands(app)

    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_extensions(app):

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Migrate
    migrate.init_app(app, db)

    # Flask-restX
    api.init_app(app)


def register_commands(app):
    for command in COMMANDS:
        app.cli.add_command(command)

# Custom error handler for 404
def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        # You can return a JSON response or render a custom HTML template
        return render_template('404.html'), 404