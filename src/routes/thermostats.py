from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, role_required
from src.models.thermostat import Thermostat, ThermostatType
from src.models.property import Property
from src.models.thermostat_log import ThermostatLog, LogType
from src.models.user import UserRole
from src.models.base import db
from datetime import datetime

thermostats_bp = Blueprint('thermostats', __name__)

# Thermostat API adapters would be implemented here in a real application
class ThermostatAPIFactory:
    @staticmethod
    def get_api(thermostat):
        """Factory method to get the appropriate API adapter for a thermostat"""
        if thermostat.type == ThermostatType.CIELO:
            return CieloAPI(thermostat)
        elif thermostat.type == ThermostatType.NEST:
            return NestAPI(thermostat)
        elif thermostat.type == ThermostatType.PIONEER:
            return PioneerAPI(thermostat)
        else:
            raise ValueError(f"Unsupported thermostat type: {thermostat.type}")

class BaseThermostatAPI:
    """Base class for thermostat API adapters"""
    def __init__(self, thermostat):
        self.thermostat = thermostat
    
    def get_status(self):
        """Get the current status of the thermostat"""
        raise NotImplementedError
    
    def set_temperature(self, temperature, is_cooling=True):
        """Set the target temperature"""
        raise NotImplementedError
    
    def turn_on(self):
        """Turn on the thermostat"""
        raise NotImplementedError
    
    def turn_off(self):
        """Turn off the thermostat"""
        raise NotImplementedError
    
    def log_action(self, message, log_type=LogType.INFO, details=None):
        """Log an action for this thermostat"""
        log = ThermostatLog(
            thermostat_id=self.thermostat.id,
            log_type=log_type,
            message=message,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log

class CieloAPI(BaseThermostatAPI):
    """API adapter for Cielo thermostats"""
    def get_status(self):
        # In a real implementation, this would call the Cielo REST API
        # For now, we'll simulate a response
        self.log_action("Retrieved status from Cielo API")
        return {
            "online": True,
            "current_temperature": 72.5,
            "target_temperature": 70.0,
            "mode": "cooling",
            "fan": "auto"
        }
    
    def set_temperature(self, temperature, is_cooling=True):
        # In a real implementation, this would call the Cielo REST API
        mode = "cooling" if is_cooling else "heating"
        self.log_action(f"Set temperature to {temperature}°F in {mode} mode")
        return True
    
    def turn_on(self):
        self.log_action("Turned on thermostat")
        return True
    
    def turn_off(self):
        self.log_action("Turned off thermostat")
        return True

class NestAPI(BaseThermostatAPI):
    """API adapter for Nest thermostats"""
    def get_status(self):
        # In a real implementation, this would call the Nest API
        self.log_action("Retrieved status from Nest API")
        return {
            "online": True,
            "current_temperature": 73.0,
            "target_temperature": 71.0,
            "mode": "cooling",
            "humidity": 45
        }
    
    def set_temperature(self, temperature, is_cooling=True):
        mode = "cooling" if is_cooling else "heating"
        self.log_action(f"Set temperature to {temperature}°F in {mode} mode")
        return True
    
    def turn_on(self):
        self.log_action("Turned on thermostat")
        return True
    
    def turn_off(self):
        self.log_action("Turned off thermostat")
        return True

class PioneerAPI(BaseThermostatAPI):
    """API adapter for Pioneer thermostats"""
    def get_status(self):
        # In a real implementation, this would use IR or smart plug control
        self.log_action("Retrieved status from Pioneer controller")
        return {
            "online": True,
            "current_temperature": 74.0,
            "target_temperature": 72.0,
            "mode": "cooling"
        }
    
    def set_temperature(self, temperature, is_cooling=True):
        mode = "cooling" if is_cooling else "heating"
        self.log_action(f"Set temperature to {temperature}°F in {mode} mode")
        return True
    
    def turn_on(self):
        self.log_action("Turned on thermostat")
        return True
    
    def turn_off(self):
        self.log_action("Turned off thermostat")
        return True

# API Routes
@thermostats_bp.route('/property/<int:property_id>', methods=['GET'])
@token_required
def get_property_thermostats(current_user, property_id):
    """Get all thermostats for a specific property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user has access to this property
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    thermostats = Thermostat.query.filter_by(property_id=property_id).all()
    
    return jsonify({
        'thermostats': [thermostat.to_dict() for thermostat in thermostats]
    }), 200

@thermostats_bp.route('/<int:thermostat_id>', methods=['GET'])
@token_required
def get_thermostat(current_user, thermostat_id):
    """Get a specific thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'thermostat': thermostat.to_dict()
    }), 200

@thermostats_bp.route('/', methods=['POST'])
@token_required
def create_thermostat(current_user):
    """Create a new thermostat"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'device_id', 'type', 'property_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if property exists and user has access
    property = Property.query.get(data['property_id'])
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Create new thermostat
    try:
        thermostat = Thermostat(
            name=data['name'],
            device_id=data['device_id'],
            type=ThermostatType(data['type']),
            property_id=data['property_id'],
            api_key=data.get('api_key'),
            ip_address=data.get('ip_address')
        )
        
        db.session.add(thermostat)
        db.session.commit()
        
        # Log the creation
        log = ThermostatLog(
            thermostat_id=thermostat.id,
            log_type=LogType.INFO,
            message=f"Thermostat created by {current_user.email}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Thermostat created successfully',
            'thermostat': thermostat.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@thermostats_bp.route('/<int:thermostat_id>', methods=['PUT'])
@token_required
def update_thermostat(current_user, thermostat_id):
    """Update a thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update thermostat fields
    if 'name' in data:
        thermostat.name = data['name']
    if 'device_id' in data:
        thermostat.device_id = data['device_id']
    if 'type' in data:
        thermostat.type = ThermostatType(data['type'])
    if 'api_key' in data:
        thermostat.api_key = data['api_key']
    if 'ip_address' in data:
        thermostat.ip_address = data['ip_address']
    
    # Admin can reassign thermostat to another property
    if current_user.role == UserRole.ADMIN and 'property_id' in data:
        # Verify property exists
        property = Property.query.get(data['property_id'])
        if not property:
            return jsonify({'error': 'Property not found'}), 404
        thermostat.property_id = data['property_id']
    
    db.session.commit()
    
    # Log the update
    log = ThermostatLog(
        thermostat_id=thermostat.id,
        log_type=LogType.INFO,
        message=f"Thermostat updated by {current_user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Thermostat updated successfully',
        'thermostat': thermostat.to_dict()
    }), 200

@thermostats_bp.route('/<int:thermostat_id>', methods=['DELETE'])
@token_required
def delete_thermostat(current_user, thermostat_id):
    """Delete a thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Log the deletion first (before the thermostat is removed)
    log = ThermostatLog(
        thermostat_id=thermostat.id,
        log_type=LogType.WARNING,
        message=f"Thermostat deleted by {current_user.email}"
    )
    db.session.add(log)
    db.session.commit()
    
    # Now delete the thermostat
    db.session.delete(thermostat)
    db.session.commit()
    
    return jsonify({
        'message': 'Thermostat deleted successfully'
    }), 200

@thermostats_bp.route('/<int:thermostat_id>/status', methods=['GET'])
@token_required
def get_thermostat_status(current_user, thermostat_id):
    """Get the current status of a thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get the appropriate API adapter
        api = ThermostatAPIFactory.get_api(thermostat)
        
        # Get status from the API
        status = api.get_status()
        
        # Update thermostat record with latest status
        thermostat.last_status = status.get('mode', 'unknown')
        thermostat.last_temperature = status.get('current_temperature')
        thermostat.last_updated = datetime.utcnow()
        thermostat.is_online = status.get('online', False)
        db.session.commit()
        
        return jsonify({
            'thermostat': thermostat.to_dict(),
            'status': status
        }), 200
    
    except Exception as e:
        # Log the error
        log = ThermostatLog(
            thermostat_id=thermostat.id,
            log_type=LogType.ERROR,
            message=f"Failed to get status: {str(e)}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'error': f'Failed to get thermostat status: {str(e)}',
            'thermostat': thermostat.to_dict()
        }), 500

@thermostats_bp.route('/<int:thermostat_id>/temperature', methods=['POST'])
@token_required
def set_thermostat_temperature(current_user, thermostat_id):
    """Set the temperature for a thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if 'temperature' not in data:
        return jsonify({'error': 'Temperature is required'}), 400
    
    try:
        temperature = float(data['temperature'])
        is_cooling = data.get('is_cooling', True)
        
        # Get the appropriate API adapter
        api = ThermostatAPIFactory.get_api(thermostat)
        
        # Set temperature via the API
        result = api.set_temperature(temperature, is_cooling)
        
        if result:
            # Update thermostat record
            thermostat.last_updated = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': f'Temperature set to {temperature}°F',
                'thermostat': thermostat.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'Failed to set temperature'
            }), 500
    
    except Exception as e:
        # Log the error
        log = ThermostatLog(
            thermostat_id=thermostat.id,
            log_type=LogType.ERROR,
            message=f"Failed to set temperature: {str(e)}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'error': f'Failed to set temperature: {str(e)}'
        }), 500

@thermostats_bp.route('/<int:thermostat_id>/power', methods=['POST'])
@token_required
def set_thermostat_power(current_user, thermostat_id):
    """Turn a thermostat on or off"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if 'power' not in data:
        return jsonify({'error': 'Power state is required (on/off)'}), 400
    
    try:
        power_on = data['power'].lower() == 'on'
        
        # Get the appropriate API adapter
        api = ThermostatAPIFactory.get_api(thermostat)
        
        # Set power state via the API
        if power_on:
            result = api.turn_on()
        else:
            result = api.turn_off()
        
        if result:
            # Update thermostat record
            thermostat.last_updated = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': f'Thermostat turned {"on" if power_on else "off"}',
                'thermostat': thermostat.to_dict()
            }), 200
        else:
            return jsonify({
                'error': f'Failed to turn thermostat {"on" if power_on else "off"}'
            }), 500
    
    except Exception as e:
        # Log the error
        log = ThermostatLog(
            thermostat_id=thermostat.id,
            log_type=LogType.ERROR,
            message=f"Failed to set power state: {str(e)}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'error': f'Failed to set power state: {str(e)}'
        }), 500

@thermostats_bp.route('/<int:thermostat_id>/logs', methods=['GET'])
@token_required
def get_thermostat_logs(current_user, thermostat_id):
    """Get logs for a specific thermostat"""
    thermostat = Thermostat.query.get_or_404(thermostat_id)
    
    # Check if user has access to this thermostat's property
    property = Property.query.get(thermostat.property_id)
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get query parameters
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get logs with pagination
    logs = ThermostatLog.query.filter_by(thermostat_id=thermostat_id) \
        .order_by(ThermostatLog.created_at.desc()) \
        .limit(limit).offset(offset).all()
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'count': len(logs),
        'limit': limit,
        'offset': offset
    }), 200
