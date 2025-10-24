from datetime import datetime
from src.extensions import db
from src.models.base import BaseModel

class SeismicEvent(db.Model, BaseModel):
    __tablename__ = "seismic_events"

    event_id = db.Column(db.Integer, primary_key=True)
    seiscomp_oid = db.Column(db.String(50))
    origin_time = db.Column(db.DateTime)
    origin_msec = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    depth = db.Column(db.Float)
    region_ge = db.Column(db.String(100))
    region_en = db.Column(db.String(100))
    area = db.Column(db.String(50))