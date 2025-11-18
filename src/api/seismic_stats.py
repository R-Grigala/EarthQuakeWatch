from datetime import datetime, timezone, timedelta

from flask_restx import Resource

from src.api.nsmodels import stats_ns, stats_model
from src.models import SeismicEvent
from src.extensions import db


@stats_ns.route('/stats')
@stats_ns.doc(
    responses={
        200: 'OK',
        500: 'Internal Server Error'
    }
)
class SeismicStatsAPI(Resource):
    @stats_ns.marshal_with(stats_model)
    def get(self):
        """Basic statistics for seismic events (24h / 7d)"""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # ბოლო 24 საათი
        q24 = SeismicEvent.query.filter(SeismicEvent.origin_time >= last_24h)
        count_24 = q24.count()
        avg_ml_24 = db.session.query(db.func.avg(SeismicEvent.ml)).filter(SeismicEvent.origin_time >= last_24h).scalar()
        max_ml_24 = db.session.query(db.func.max(SeismicEvent.ml)).filter(SeismicEvent.origin_time >= last_24h).scalar()

        # ბოლო 7 დღე
        q7 = SeismicEvent.query.filter(SeismicEvent.origin_time >= last_7d)
        count_7 = q7.count()
        avg_ml_7 = db.session.query(db.func.avg(SeismicEvent.ml)).filter(SeismicEvent.origin_time >= last_7d).scalar()

        return {
            "count_last_24h": count_24 or 0,
            "avg_ml_last_24h": float(avg_ml_24) if avg_ml_24 is not None else None,
            "max_ml_last_24h": float(max_ml_24) if max_ml_24 is not None else None,
            "count_last_7d": count_7 or 0,
            "avg_ml_last_7d": float(avg_ml_7) if avg_ml_7 is not None else None,
        }, 200
