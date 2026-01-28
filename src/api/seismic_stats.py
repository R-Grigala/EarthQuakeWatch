from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from flask_restx import Resource

from src.api.nsmodels import stats_ns, stats_model
from src.models import SeismicEvent


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
        """Return basic seismic statistics for different time windows"""

        # Current UTC time
        now = datetime.now(timezone.utc)

        # Time windows for statistics
        windows = {
            "1m": now - relativedelta(months=1),
            "6m": now - relativedelta(months=6),
            "1y": now - relativedelta(years=1),
        }

        stats = {}

        # Calculate stats for each time window
        for key, since in windows.items():
            # Total event count and maximum magnitude
            count, max_ml = (
                SeismicEvent.query
                .with_entities(
                    func.count(SeismicEvent.event_id),
                    func.max(SeismicEvent.ml),
                )
                .filter(SeismicEvent.origin_time >= since)
                .one()
            )

            if not count:
                # No events in this window
                stats[key] = {
                    "count": 0,
                    "avg_ml": 0.0,
                    "max_ml": 0.0,
                }
                continue

            # Offset for median (used as average magnitude here)
            offset = count // 2

            # Median magnitude (ordered by ML)
            midl = (
                SeismicEvent.query
                .with_entities(SeismicEvent.ml)
                .filter(
                    SeismicEvent.origin_time >= since,
                    SeismicEvent.ml.isnot(None)
                )
                .order_by(SeismicEvent.ml.asc())
                .offset(offset)
                .limit(1)
                .scalar()
            )

            stats[key] = {
                "count": int(count or 0),
                "avg_ml": float(midl) if midl is not None else 0.0,
                "max_ml": float(max_ml) if max_ml is not None else 0.0,
            }

        # Total number of events in the database
        total_events = (
            SeismicEvent.query
            .with_entities(func.count(SeismicEvent.event_id))
            .scalar()
        ) or 0

        # Last update timestamp (UTC)
        updated_utc = (
            SeismicEvent.query
            .with_entities(func.max(SeismicEvent.created_at))
            .scalar()
        )

        # API response
        return {
            "count_last_1m": stats["1m"]["count"],
            "avg_ml_last_1m": stats["1m"]["avg_ml"],
            "max_ml_last_1m": stats["1m"]["max_ml"],

            "count_last_6m": stats["6m"]["count"],
            "avg_ml_last_6m": stats["6m"]["avg_ml"],
            "max_ml_last_6m": stats["6m"]["max_ml"],

            "count_last_1y": stats["1y"]["count"],
            "avg_ml_last_1y": stats["1y"]["avg_ml"],
            "max_ml_last_1y": stats["1y"]["max_ml"],

            "total_events": int(total_events),
            "updated_utc": updated_utc,
        }, 200