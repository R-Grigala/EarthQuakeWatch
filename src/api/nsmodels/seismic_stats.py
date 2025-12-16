from flask_restx import reqparse, fields
from src.extensions import api

stats_ns = api.namespace('Stats', description='Analytics and statistics for seismic events', path='/api')

stats_model = stats_ns.model(
    "SeismicStats",
    {
        "count_last_24h": fields.Integer,
        "avg_ml_last_24h": fields.Float,
        "max_ml_last_24h": fields.Float,

        "count_last_7d": fields.Integer,
        "avg_ml_last_7d": fields.Float,

        "count_last_1y": fields.Integer,
        "avg_ml_last_1y": fields.Float,
        "max_ml_last_1y": fields.Float,
        
        "total_events": fields.Integer,
        "updated_utc": fields.String,
    }
)
