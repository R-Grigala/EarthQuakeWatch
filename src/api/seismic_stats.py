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
        """Basic statistics for seismic events (24h / 7d / 1y)"""

        now = datetime.now(timezone.utc)

        windows = {
            "24h": now - timedelta(hours=24),
            "7d": now - timedelta(days=7),
            "1y": now - timedelta(days=365),
        }

        stats = {}

        for key, since in windows.items():
            q = SeismicEvent.query.filter(SeismicEvent.origin_time >= since)

            count = q.count()

            avg_ml = (
                db.session
                .query(db.func.avg(SeismicEvent.ml))
                .filter(SeismicEvent.origin_time >= since)
                .scalar()
            )

            max_ml = (
                db.session
                .query(db.func.max(SeismicEvent.ml))
                .filter(SeismicEvent.origin_time >= since)
                .scalar()
            )

            stats[key] = {
                "count": count or 0,
                "avg_ml": float(avg_ml) if avg_ml is not None else 0,
                "max_ml": float(max_ml) if max_ml is not None else 0,
            }

        # Total events in DB
        total_events = db.session.query(db.func.count(SeismicEvent.event_id)).scalar() or 0

        # Updated timestamp from last inserted row (created_at)
        updated_utc = db.session.query(db.func.max(SeismicEvent.created_at)).scalar()

        return {
            "count_last_24h": stats["24h"]["count"],
            "avg_ml_last_24h": stats["24h"]["avg_ml"],
            "max_ml_last_24h": stats["24h"]["max_ml"],

            "count_last_7d": stats["7d"]["count"],
            "avg_ml_last_7d": stats["7d"]["avg_ml"],

            "count_last_1y": stats["1y"]["count"],
            "avg_ml_last_1y": stats["1y"]["avg_ml"],
            "max_ml_last_1y": stats["1y"]["max_ml"],

            "total_events": int(total_events),
            "updated_utc": updated_utc,
        }, 200
