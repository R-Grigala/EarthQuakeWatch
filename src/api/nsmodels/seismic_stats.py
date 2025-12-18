from flask_restx import fields
from src.extensions import api

stats_ns = api.namespace(
    'Stats',
    description='Analytics and statistics for seismic events',
    path='/api'
)

stats_model = stats_ns.model(
    "SeismicStats",
    {
        "count_last_1m": fields.Integer(description="Number of events in last 1 month"),
        "avg_ml_last_1m": fields.Float(description="Average ML in last 1 month"),
        "max_ml_last_1m": fields.Float(description="Maximum ML in last 1 month"),

        "count_last_6m": fields.Integer(description="Number of events in last 6 months"),
        "avg_ml_last_6m": fields.Float(description="Average ML in last 6 months"),
        "max_ml_last_6m": fields.Float(description="Maximum ML in last 6 months"),

        "count_last_1y": fields.Integer(description="Number of events in last 1 year"),
        "avg_ml_last_1y": fields.Float(description="Average ML in last 1 year"),
        "max_ml_last_1y": fields.Float(description="Maximum ML in last 1 year"),

        "total_events": fields.Integer(description="Total number of events in database"),
        "updated_utc": fields.String(description="UTC timestamp of last inserted event"),
    }
)
