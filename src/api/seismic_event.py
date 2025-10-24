from flask_restx import Resource

from src.api.nsmodels import event_ns, event_model
from src.models import SeismicEvent

@event_ns.route('/events')
@event_ns.doc(responses={200: 'OK', 400: 'Invalid Argument', 401: 'JWT Token Expires', 403: 'Unauthorized', 404: 'Not Found'})
class SeismicListAPI(Resource):
    @event_ns.marshal_list_with(event_model)
    def get(self):
        """List all seismic events"""
        events = SeismicEvent.query.all()
        if not events:
            return {"error": "მიწისძვრები არ მოიძებნა."}, 404

        return events

    @event_ns.expect(event_model)
    @event_ns.doc(security='ApiKeyAuth', responses={201: 'Created', 401: 'Unauthorized'})
    def post(self):
        """Add a new seismic event (requires API key)"""
        api_key = request.headers.get('X-API-Key')
        if api_key != Config.API_KEY:
            return {'error': 'Unauthorized - Invalid API key'}, 401

        # --- Parse request body ---
        args = event_parser.parse_args()

        # --- Convert origin_time ---
        try:
            origin_time = datetime.datetime.fromisoformat(args['origin_time'])
        except Exception:
            return {'error': 'Invalid origin_time format (use ISO 8601, e.g. 2025-10-24T12:20:00)'}, 400

        # --- Check if event already exists ---
        existing = SeismicEvent.query.filter_by(event_id=args['event_id']).first()
        if existing:
            return {'error': f'Event with ID {args["event_id"]} already exists.'}, 400

        # --- Create a new SeismicEvent object ---
        new_event = SeismicEvent(
            event_id=args['event_id'],
            seiscomp_oid=args.get('seiscomp_oid'),
            origin_time=origin_time,
            origin_msec=args.get('origin_msec'),
            latitude=args['latitude'],
            longitude=args['longitude'],
            depth=args['depth'],
            region_ge=args.get('region_ge'),
            region_en=args.get('region_en'),
            area=args.get('area')
        )
        # --- Commit to database ---
        new_event.create()

        return {
            'status': 'success',
            'message': 'Seismic event added successfully',
            'event_id': new_event.event_id
        }, 201
