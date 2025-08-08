from flask import Blueprint, request, jsonify
from src.routes.auth import token_required, role_required
from src.models.property import Property
from src.models.user import User, UserRole
from src.models.base import db

properties_bp = Blueprint('properties', __name__)

@properties_bp.route('/', methods=['GET'])
@token_required
def get_properties(current_user):
    """Get all properties for the current user"""
    # Admin can see all properties, others only see their own
    if current_user.role == UserRole.ADMIN:
        properties = Property.query.all()
    else:
        properties = Property.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'properties': [prop.to_dict() for prop in properties]
    }), 200

@properties_bp.route('/<int:property_id>', methods=['GET'])
@token_required
def get_property(current_user, property_id):
    """Get a specific property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user has access to this property
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'property': property.to_dict()
    }), 200

@properties_bp.route('/', methods=['POST'])
@token_required
def create_property(current_user):
    """Create a new property"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'address', 'city', 'state', 'zip_code', 'country']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new property
    property = Property(
        name=data['name'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        country=data['country'],
        user_id=current_user.id
    )
    
    db.session.add(property)
    db.session.commit()
    
    return jsonify({
        'message': 'Property created successfully',
        'property': property.to_dict()
    }), 201

@properties_bp.route('/<int:property_id>', methods=['PUT'])
@token_required
def update_property(current_user, property_id):
    """Update a property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user has access to this property
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update property fields
    if 'name' in data:
        property.name = data['name']
    if 'address' in data:
        property.address = data['address']
    if 'city' in data:
        property.city = data['city']
    if 'state' in data:
        property.state = data['state']
    if 'zip_code' in data:
        property.zip_code = data['zip_code']
    if 'country' in data:
        property.country = data['country']
    
    # Admin can reassign property to another user
    if current_user.role == UserRole.ADMIN and 'user_id' in data:
        # Verify user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        property.user_id = data['user_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Property updated successfully',
        'property': property.to_dict()
    }), 200

@properties_bp.route('/<int:property_id>', methods=['DELETE'])
@token_required
def delete_property(current_user, property_id):
    """Delete a property"""
    property = Property.query.get_or_404(property_id)
    
    # Check if user has access to this property
    if current_user.role != UserRole.ADMIN and property.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(property)
    db.session.commit()
    
    return jsonify({
        'message': 'Property deleted successfully'
    }), 200
