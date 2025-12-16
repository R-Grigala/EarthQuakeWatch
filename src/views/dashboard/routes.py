from flask import render_template, Blueprint
from os import path

from src.config import Config

TEMPLATES_FOLDER = path.join(Config.BASE_DIR, Config.TEMPLATES_FOLDERS, "dashboard")
dashboard_blueprint = Blueprint("dashboard", __name__, template_folder=TEMPLATES_FOLDER)

@dashboard_blueprint.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")