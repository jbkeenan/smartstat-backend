from src.models.base import db, BaseModel
from src.models.thermostat import Thermostat
import enum

class LogType(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class ThermostatLog(db.Model, BaseModel):
    """Log model for storing thermostat activity logs"""
    __tablename__ = 'thermostat_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    thermostat_id = db.Column(db.Integer, db.ForeignKey('thermostats.id'), nullable=False)
    log_type = db.Column(db.Enum(LogType), nullable=False, default=LogType.INFO)
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON, nullable=True)  # Additional JSON details
    
    # Relationships
    thermostat = db.relationship('Thermostat', back_populates='logs')
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'id': self.id,
            'thermostat_id': self.thermostat_id,
            'log_type': self.log_type.value,
            'message': self.message,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
