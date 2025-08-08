from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, role_required
from src.models.user import UserRole
from src.models.thermostat_log import ThermostatLog, LogType
from src.models.property import Property
from src.models.thermostat import Thermostat
from src.models.base import db
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/logs', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def get_all_logs():
    """Get all system logs (admin only)"""
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    log_type = request.args.get('log_type')
    property_id = request.args.get('property_id')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Base query
    query = ThermostatLog.query
    
    # Apply filters if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(ThermostatLog.created_at >= start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(ThermostatLog.created_at <= end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    if log_type:
        try:
            log_type = LogType(log_type)
            query = query.filter(ThermostatLog.log_type == log_type)
        except:
            return jsonify({'error': f'Invalid log_type. Must be one of: {", ".join([t.value for t in LogType])}'}), 400
    
    if property_id:
        # Get all thermostats for the property
        thermostats = Thermostat.query.filter_by(property_id=property_id).all()
        thermostat_ids = [t.id for t in thermostats]
        query = query.filter(ThermostatLog.thermostat_id.in_(thermostat_ids))
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    logs = query.order_by(ThermostatLog.created_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'count': len(logs),
        'total_count': total_count,
        'limit': limit,
        'offset': offset
    }), 200

@admin_bp.route('/logs/export', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def export_logs():
    """Export logs as CSV (admin only)"""
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    log_type = request.args.get('log_type')
    property_id = request.args.get('property_id')
    
    # Base query
    query = ThermostatLog.query
    
    # Apply filters if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(ThermostatLog.created_at >= start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(ThermostatLog.created_at <= end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    if log_type:
        try:
            log_type = LogType(log_type)
            query = query.filter(ThermostatLog.log_type == log_type)
        except:
            return jsonify({'error': f'Invalid log_type. Must be one of: {", ".join([t.value for t in LogType])}'}), 400
    
    if property_id:
        # Get all thermostats for the property
        thermostats = Thermostat.query.filter_by(property_id=property_id).all()
        thermostat_ids = [t.id for t in thermostats]
        query = query.filter(ThermostatLog.thermostat_id.in_(thermostat_ids))
    
    # Get all logs
    logs = query.order_by(ThermostatLog.created_at.desc()).all()
    
    # Generate CSV content
    csv_content = "id,thermostat_id,log_type,message,created_at\n"
    for log in logs:
        csv_content += f"{log.id},{log.thermostat_id},{log.log_type.value},\"{log.message}\",{log.created_at.isoformat()}\n"
    
    # Return CSV response
    response = jsonify({
        'csv': csv_content,
        'count': len(logs)
    })
    
    return response, 200

@admin_bp.route('/alerts', methods=['GET'])
@token_required
def get_alerts(current_user):
    """Get system alerts"""
    # For non-admin users, only show alerts for their properties
    if current_user.role != UserRole.ADMIN:
        properties = Property.query.filter_by(user_id=current_user.id).all()
        property_ids = [p.id for p in properties]
        thermostats = Thermostat.query.filter(Thermostat.property_id.in_(property_ids)).all()
    else:
        thermostats = Thermostat.query.all()
    
    thermostat_ids = [t.id for t in thermostats]
    
    # Get recent error logs
    recent_time = datetime.utcnow() - timedelta(hours=24)
    error_logs = ThermostatLog.query.filter(
        ThermostatLog.thermostat_id.in_(thermostat_ids),
        ThermostatLog.log_type == LogType.ERROR,
        ThermostatLog.created_at >= recent_time
    ).order_by(ThermostatLog.created_at.desc()).all()
    
    # Get offline thermostats
    offline_thermostats = []
    for thermostat in thermostats:
        if not thermostat.is_online:
            property = Property.query.get(thermostat.property_id)
            offline_thermostats.append({
                'thermostat': thermostat.to_dict(),
                'property': property.to_dict()
            })
    
    return jsonify({
        'error_logs': [log.to_dict() for log in error_logs],
        'offline_thermostats': offline_thermostats
    }), 200

@admin_bp.route('/system/status', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN])
def get_system_status():
    """Get system status information (admin only)"""
    # Count users
    user_count = db.session.query(db.func.count(db.distinct(Property.user_id))).scalar()
    
    # Count properties
    property_count = db.session.query(db.func.count(Property.id)).scalar()
    
    # Count thermostats
    thermostat_count = db.session.query(db.func.count(Thermostat.id)).scalar()
    
    # Count online thermostats
    online_thermostat_count = db.session.query(db.func.count(Thermostat.id)).filter(Thermostat.is_online == True).scalar()
    
    # Count logs in last 24 hours
    recent_time = datetime.utcnow() - timedelta(hours=24)
    recent_log_count = db.session.query(db.func.count(ThermostatLog.id)).filter(ThermostatLog.created_at >= recent_time).scalar()
    
    # Count error logs in last 24 hours
    recent_error_count = db.session.query(db.func.count(ThermostatLog.id)).filter(
        ThermostatLog.log_type == LogType.ERROR,
        ThermostatLog.created_at >= recent_time
    ).scalar()
    
    return jsonify({
        'user_count': user_count,
        'property_count': property_count,
        'thermostat_count': thermostat_count,
        'online_thermostat_count': online_thermostat_count,
        'online_percentage': (online_thermostat_count / thermostat_count * 100) if thermostat_count > 0 else 0,
        'recent_log_count': recent_log_count,
        'recent_error_count': recent_error_count,
        'error_percentage': (recent_error_count / recent_log_count * 100) if recent_log_count > 0 else 0,
        'timestamp': datetime.utcnow().isoformat()
    }), 200
