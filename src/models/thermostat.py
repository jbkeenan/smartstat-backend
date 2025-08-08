from src.models.base import db, BaseModel
from src.models.property import Property
import enum

class ThermostatType(enum.Enum):
    CIELO = "cielo"
    NEST = "nest"
    PIONEER = "pioneer"

class Thermostat(db.Model, BaseModel):
    """Thermostat model for storing thermostat information"""
    __tablename__ = 'thermostats'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(ThermostatType), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Device-specific fields
    api_key = db.Column(db.String(255), nullable=True)  # For API authentication
    ip_address = db.Column(db.String(50), nullable=True)  # For local network devices
    last_status = db.Column(db.String(50), nullable=True)  # Last known status
    last_temperature = db.Column(db.Float, nullable=True)  # Last known temperature
    last_updated = db.Column(db.DateTime, nullable=True)  # Last status update time
    is_online = db.Column(db.Boolean, default=False)  # Device online status
    
    # Relationships
    property = db.relationship('Property', back_populates='thermostats')
    schedules = db.relationship('Schedule', back_populates='thermostat', lazy='dynamic')
    logs = db.relationship('ThermostatLog', back_populates='thermostat', lazy='dynamic')
    
    def to_dict(self):
        """Convert thermostat to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'device_id': self.device_id,
            'type': self.type.value,
            'property_id': self.property_id,
            'api_key': self.api_key,
            'ip_address': self.ip_address,
            'last_status': self.last_status,
            'last_temperature': self.last_temperature,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_online': self.is_online,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
