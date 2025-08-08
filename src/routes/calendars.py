from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, role_required
from src.models.calendar import Calendar
from src.models.booking import Booking
from src.models.property import Property
from src.models.user import UserRole
from src.models.base import db
from datetime import datetime
import requests
import icalendar
import recurring_ical_events
from dateutil import rrule, parser

calendars_bp = Blueprint('calendars', __name__)

# Calendar API adapters
class CalendarAPIFactory:
    @staticmethod
    def get_api(calendar):
        """Factory method to get the appropriate API adapter for a calendar"""
        if calendar.source_type == 'google':
            return GoogleCalendarAPI(calendar)
        elif calendar.source_type == 'ical':
            return ICalAPI(calendar)
        else:
            raise ValueError(f"Unsupported calendar type: {calendar.source_type}")

class BaseCalendarAPI:
    """Base class for calendar API adapters"""
    def __init__(self, calendar):
        self.calendar = calendar
    
    def sync(self, start_date=None, end_date=None):
        """Sync bookings from the calendar source"""
        raise NotImplementedError

class GoogleCalendarAPI(BaseCalendarAPI):
    """API adapter for Google Calendar"""
    def sync(self, start_date=None, end_date=None):
        """Sync bookings from Google Calendar"""
        # In a real implementation, this would use the Google Calendar API
        # For now, we'll simulate a response
        
        # Update last synced timestamp
        self.calendar.last_synced = datetime.utcnow()
        db.session.commit()
        
        # Return simulated bookings
        return [
            {
                "guest_name": "John Doe",
                "check_in": datetime.utcnow().replace(hour=15, minute=0, second=0, microsecond=0),
                "check_out": datetime.utcnow().replace(day=datetime.utcnow().day + 3, hour=11, minute=0, second=0, microsecond=0),
                "booking_reference": "G12345",
                "source": "airbnb"
            },
            {
                "guest_name": "Jane Smith",
                "check_in": datetime.utcnow().replace(day=datetime.utcnow().day + 5, hour=15, minute=0, second=0, microsecond=0),
                "check_out": datetime.utcnow().replace(day=datetime.utcnow().day + 8, hour=11, minute=0, second=0, microsecond=0),
                "booking_reference": "G67890",
                "source": "vrbo"
            }
        ]

class ICalAPI(BaseCalendarAPI):
    """API adapter for iCal calendars"""
    def sync(self, start_date=None, end_date=None):
        """Sync bookings from iCal feed"""
        try:
            # In a real implementation, this would fetch and parse the iCal feed
            # For now, we'll simulate the process
            
            # Simulate fetching iCal data
            # response = requests.get(self.calendar.source_url)
            # ical_data = response.text
            
            # Parse iCal data
            # cal = icalendar.Calendar.from_ical(ical_data)
            
            # Get events in date range
            # if not start_date:
            #     start_date = datetime.utcnow()
            # if not end_date:
            #     end_date = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            
            # events = recurring_ical_events.of(cal).between(start_date, end_date)
            
            # Update last synced timestamp
            self.calendar.last_synced = datetime.utcnow()
            db.session.commit()
            
            # Return simulated bookings
            return [
                {
                    "guest_name": "iCal Guest",
                    "check_in": datetime.utcnow().replace(day=datetime.utcnow().day + 10, hour=15, minute=0, second=0, microsecond=0),
                    "check_out": datetime.utcnow().replace(day=datetime.utcnow().day + 15, hour=11, minute=0, second=0, microsecond=0),
                    "booking_reference": "ICAL123",
                    "source": "airbnb"
                }
            ]
        except Exception as e:
            # Log error and return empty list
            print(f"Error syncing iCal calendar: {str(e)}")
            return []

# API Routes
@calendars_bp.route('/property/<int:property_id>', methods=['GET'])
@token_required
def get_property_calendars(current_user, property_id):
    """Get all calendars for a specific property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user has access to this property
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    calendars = Calendar.query.filter_by(property_id=property_id).all()
    
    return jsonify({
        'calendars': [calendar.to_dict() for calendar in calendars]
    }), 200

@calendars_bp.route('/<int:calendar_id>', methods=['GET'])
@token_required
def get_calendar(current_user, calendar_id):
    """Get a specific calendar"""
    calendar = Calendar.query.get_or_404(calendar_id)
    
    # Check if user has access to this calendar's property
    property = Property.query.get(calendar.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'calendar': calendar.to_dict()
    }), 200

@calendars_bp.route('/', methods=['POST'])
@token_required
def create_calendar(current_user):
    """Create a new calendar"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'source_type', 'source_url', 'property_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if property exists and user has access
    property = Property.query.get(data['property_id'])
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Validate source type
    valid_source_types = ['google', 'ical']
    if data['source_type'] not in valid_source_types:
        return jsonify({'error': f'Invalid source type. Must be one of: {", ".join(valid_source_types)}'}), 400
    
    # Create new calendar
    calendar = Calendar(
        name=data['name'],
        source_type=data['source_type'],
        source_url=data['source_url'],
        property_id=data['property_id']
    )
    
    db.session.add(calendar)
    db.session.commit()
    
    return jsonify({
        'message': 'Calendar created successfully',
        'calendar': calendar.to_dict()
    }), 201

@calendars_bp.route('/<int:calendar_id>', methods=['PUT'])
@token_required
def update_calendar(current_user, calendar_id):
    """Update a calendar"""
    calendar = Calendar.query.get_or_404(calendar_id)
    
    # Check if user has access to this calendar's property
    property = Property.query.get(calendar.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update calendar fields
    if 'name' in data:
        calendar.name = data['name']
    if 'source_url' in data:
        calendar.source_url = data['source_url']
    if 'source_type' in data:
        # Validate source type
        valid_source_types = ['google', 'ical']
        if data['source_type'] not in valid_source_types:
            return jsonify({'error': f'Invalid source type. Must be one of: {", ".join(valid_source_types)}'}), 400
        calendar.source_type = data['source_type']
    
    # Admin can reassign calendar to another property
    if current_user.role == UserRole.ADMIN and 'property_id' in data:
        # Verify property exists
        property = Property.query.get(data['property_id'])
        if not property:
            return jsonify({'error': 'Property not found'}), 404
        calendar.property_id = data['property_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Calendar updated successfully',
        'calendar': calendar.to_dict()
    }), 200

@calendars_bp.route('/<int:calendar_id>', methods=['DELETE'])
@token_required
def delete_calendar(current_user, calendar_id):
    """Delete a calendar"""
    calendar = Calendar.query.get_or_404(calendar_id)
    
    # Check if user has access to this calendar's property
    property = Property.query.get(calendar.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Delete associated bookings first
    Booking.query.filter_by(calendar_id=calendar_id).delete()
    
    # Now delete the calendar
    db.session.delete(calendar)
    db.session.commit()
    
    return jsonify({
        'message': 'Calendar deleted successfully'
    }), 200

@calendars_bp.route('/<int:calendar_id>/sync', methods=['POST'])
@token_required
def sync_calendar(current_user, calendar_id):
    """Sync bookings from a calendar source"""
    calendar = Calendar.query.get_or_404(calendar_id)
    
    # Check if user has access to this calendar's property
    property = Property.query.get(calendar.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get date range from request (optional)
        data = request.get_json() or {}
        start_date = parser.parse(data['start_date']) if 'start_date' in data else None
        end_date = parser.parse(data['end_date']) if 'end_date' in data else None
        
        # Get the appropriate API adapter
        api = CalendarAPIFactory.get_api(calendar)
        
        # Sync bookings from the calendar source
        bookings_data = api.sync(start_date, end_date)
        
        # Process bookings
        new_bookings = []
        for booking_data in bookings_data:
            # Check if booking already exists (by reference or date range)
            existing_booking = None
            if 'booking_reference' in booking_data and booking_data['booking_reference']:
                existing_booking = Booking.query.filter_by(
                    calendar_id=calendar.id,
                    booking_reference=booking_data['booking_reference']
                ).first()
            
            if not existing_booking:
                # Check for overlapping bookings by date
                existing_booking = Booking.query.filter_by(calendar_id=calendar.id).filter(
                    Booking.check_in <= booking_data['check_out'],
                    Booking.check_out >= booking_data['check_in']
                ).first()
            
            if existing_booking:
                # Update existing booking
                existing_booking.guest_name = booking_data.get('guest_name', existing_booking.guest_name)
                existing_booking.check_in = booking_data['check_in']
                existing_booking.check_out = booking_data['check_out']
                existing_booking.booking_reference = booking_data.get('booking_reference', existing_booking.booking_reference)
                existing_booking.source = booking_data.get('source', existing_booking.source)
            else:
                # Create new booking
                new_booking = Booking(
                    calendar_id=calendar.id,
                    guest_name=booking_data.get('guest_name'),
                    check_in=booking_data['check_in'],
                    check_out=booking_data['check_out'],
                    booking_reference=booking_data.get('booking_reference'),
                    source=booking_data.get('source')
                )
                db.session.add(new_booking)
                new_bookings.append(new_booking)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'message': f'Calendar synced successfully. {len(new_bookings)} new bookings created.',
            'calendar': calendar.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to sync calendar: {str(e)}'
        }), 500

@calendars_bp.route('/<int:calendar_id>/bookings', methods=['GET'])
@token_required
def get_calendar_bookings(current_user, calendar_id):
    """Get all bookings for a specific calendar"""
    calendar = Calendar.query.get_or_404(calendar_id)
    
    # Check if user has access to this calendar's property
    property = Property.query.get(calendar.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = Booking.query.filter_by(calendar_id=calendar_id)
    
    # Apply date filters if provided
    if start_date:
        try:
            start_date = parser.parse(start_date)
            query = query.filter(Booking.check_out >= start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = parser.parse(end_date)
            query = query.filter(Booking.check_in <= end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Execute query
    bookings = query.order_by(Booking.check_in).all()
    
    return jsonify({
        'bookings': [booking.to_dict() for booking in bookings],
        'count': len(bookings)
    }), 200
