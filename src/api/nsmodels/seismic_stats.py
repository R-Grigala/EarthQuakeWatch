from flask_restx import reqparse, fields
from src.extensions import api

stats_ns = api.namespace('Stats', description='Analytics and statistics for seismic events', path='/api')

stats_model = api.model('SeismicStats', {
    'count_last_24h': fields.Integer(description='Number of events in last 24 hours'),
    'avg_ml_last_24h': fields.Float(description='Average ML in last 24 hours'),
    'max_ml_last_24h': fields.Float(description='Maximum ML in last 24 hours'),
    'count_last_7d': fields.Integer(description='Number of events in last 7 days'),
    'avg_ml_last_7d': fields.Float(description='Average ML in last 7 days'),
})