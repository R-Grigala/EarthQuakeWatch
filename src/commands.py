from flask.cli import with_appcontext
import click
from datetime import datetime

from src.extensions import db
from src.models import SeismicEvent

@click.command("init_db")
@with_appcontext
def init_db():
    click.echo("Creating Database")
    db.drop_all()
    db.create_all()
    click.echo("Database Created")

@click.command("populate_db")
@with_appcontext
def populate_db():
    click.echo("Populating Database with sample seismic events...")
    new_event = SeismicEvent(
        event_id=566058,
        seiscomp_oid="oid123",
        origin_time=datetime(2025, 8, 15, 12, 0, 0),
        origin_msec=123,
        latitude=40.7128,
        longitude=-74.0060,
        depth=10.0,
        region_ge="RegionGE",
        region_en="RegionEN",
        area="local",
        ml=3.5
    )
    new_event.create()