from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, role_required
from src.models.schedule import Schedule, ScheduleType
from src.models.thermostat import Thermostat
from src.models.property import Property
from src.models.user import UserRole
from src.models.base import db
from datetime import datetime, timedelta

schedules_bp = Blueprint('schedules', __name__)

@schedules_bp.route('/thermostat/<int:thermostat_id>', methods=['GET'])
@token_required
def get_thermostat_schedules(current_user, thermostat_id):
    """Get all schedules for a specific thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    schedules = Schedule.query.filter_by(thermostat_id=thermostat_id).all()
    
    return jsonify({
        'schedules': [schedule.to_dict() for schedule in schedules]
    }), 200

@schedules_bp.route('/<int:schedule_id>', methods=['GET'])
@token_required
def get_schedule(current_user, schedule_id):
    """Get a specific schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check if user has access to this schedule's thermostat
    thermostat = Thermostat.query.get(schedule.thermostat_id)
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'schedule': schedule.to_dict()
    }), 200

@schedules_bp.route('/', methods=['POST'])
@token_required
def create_schedule(current_user):
    """Create a new schedule"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['thermostat_id', 'schedule_type', 'target_temperature']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if thermostat exists and user has access
    thermostat = Thermostat.query.get(data['thermostat_id'])
    if not thermostat:
        return jsonify({'error': 'Thermostat not found'}), 404
    
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Validate schedule type
    try:
        schedule_type = ScheduleType(data['schedule_type'])
    except ValueError:
        return jsonify({'error': f'Invalid schedule type. Must be one of: {", ".join([t.value for t in ScheduleType])}'}), 400
    
    # Validate type-specific fields
    if schedule_type == ScheduleType.CHECK_IN and 'hours_before_checkin' not in data:
        return jsonify({'error': 'hours_before_checkin is required for CHECK_IN schedule type'}), 400
    
    if schedule_type == ScheduleType.CHECK_OUT and 'hours_after_checkout' not in data:
        return jsonify({'error': 'hours_after_checkout is required for CHECK_OUT schedule type'}), 400
    
    if schedule_type == ScheduleType.MANUAL and ('start_time' not in data or 'end_time' not in data):
        return jsonify({'error': 'start_time and end_time are required for MANUAL schedule type'}), 400
    
    # Create new schedule
    try:
        schedule = Schedule(
            thermostat_id=data['thermostat_id'],
            schedule_type=schedule_type,
            target_temperature=float(data['target_temperature']),
            is_cooling=data.get('is_cooling', True),
            is_active=data.get('is_active', True)
        )
        
        # Set type-specific fields
        if schedule_type == ScheduleType.CHECK_IN:
            schedule.hours_before_checkin = int(data['hours_before_checkin'])
        
        if schedule_type == ScheduleType.CHECK_OUT:
            schedule.hours_after_checkout = int(data['hours_after_checkout'])
        
        if schedule_type == ScheduleType.MANUAL:
            schedule.start_time = datetime.fromisoformat(data['start_time'])
            schedule.end_time = datetime.fromisoformat(data['end_time'])
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create schedule: {str(e)}'}), 500

@schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
@token_required
def update_schedule(current_user, schedule_id):
    """Update a schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check if user has access to this schedule's thermostat
    thermostat = Thermostat.query.get(schedule.thermostat_id)
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update schedule fields
    if 'target_temperature' in data:
        schedule.target_temperature = float(data['target_temperature'])
    
    if 'is_cooling' in data:
        schedule.is_cooling = data['is_cooling']
    
    if 'is_active' in data:
        schedule.is_active = data['is_active']
    
    # Update type-specific fields
    if 'hours_before_checkin' in data and schedule.schedule_type == ScheduleType.CHECK_IN:
        schedule.hours_before_checkin = int(data['hours_before_checkin'])
    
    if 'hours_after_checkout' in data and schedule.schedule_type == ScheduleType.CHECK_OUT:
        schedule.hours_after_checkout = int(data['hours_after_checkout'])
    
    if schedule.schedule_type == ScheduleType.MANUAL:
        if 'start_time' in data:
            schedule.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            schedule.end_time = datetime.fromisoformat(data['end_time'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Schedule updated successfully',
        'schedule': schedule.to_dict()
    }), 200

@schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
@token_required
def delete_schedule(current_user, schedule_id):
    """Delete a schedule"""
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Check if user has access to this schedule's thermostat
    thermostat = Thermostat.query.get(schedule.thermostat_id)
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(schedule)
    db.session.commit()
    
    return jsonify({
        'message': 'Schedule deleted successfully'
    }), 200

@schedules_bp.route('/upcoming', methods=['GET'])
@token_required
def get_upcoming_schedules(current_user):
    """Get upcoming schedule triggers for the user's thermostats"""
    # Get all properties for the user
    if current_user.role == UserRole.ADMIN:
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(user_id=current_user.id).all()
    
    property_ids = [p.id for p in properties]
    
    # Get all thermostats for these properties
    thermostats = Thermostat.query.filter(Thermostat.property_id.in_(property_ids)).all()
    thermostat_ids = [t.id for t in thermostats]
    
    # Get all active schedules for these thermostats
    schedules = Schedule.query.filter(
        Schedule.thermostat_id.in_(thermostat_ids),
        Schedule.is_active == True
    ).all()
    
    # For manual schedules, filter to only include upcoming ones
    now = datetime.utcnow()
    upcoming_schedules = []
    
    for schedule in schedules:
        if schedule.schedule_type == ScheduleType.MANUAL:
            if schedule.end_time > now:
                upcoming_schedules.append({
                    'schedule': schedule.to_dict(),
                    'thermostat': Thermostat.query.get(schedule.thermostat_id).to_dict(),
                    'property': Property.query.get(Thermostat.query.get(schedule.thermostat_id).property_id).to_dict(),
                    'trigger_time': schedule.start_time.isoformat() if schedule.start_time > now else 'In progress',
                    'end_time': schedule.end_time.isoformat()
                })
        else:
            # For non-manual schedules, we'd need to calculate based on bookings
            # This is simplified for the prototype
            upcoming_schedules.append({
                'schedule': schedule.to_dict(),
                'thermostat': Thermostat.query.get(schedule.thermostat_id).to_dict(),
                'property': Property.query.get(Thermostat.query.get(schedule.thermostat_id).property_id).to_dict(),
                'trigger_time': 'Based on bookings',
                'end_time': 'Based on bookings'
            })
    
    return jsonify({
        'upcoming_schedules': upcoming_schedules
    }), 200
