from src.models.base import db, BaseModel
from src.models.thermostat import Thermostat
import enum

class ScheduleType(enum.Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    VACANCY = "vacancy"
    MANUAL = "manual"

class Schedule(db.Model, BaseModel):
    """Schedule model for storing automation schedules"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    thermostat_id = db.Column(db.Integer, db.ForeignKey('thermostats.id'), nullable=False)
    schedule_type = db.Column(db.Enum(ScheduleType), nullable=False)
    
    # Schedule settings
    hours_before_checkin = db.Column(db.Integer, nullable=True)  # For CHECK_IN type
    hours_after_checkout = db.Column(db.Integer, nullable=True)  # For CHECK_OUT type
    target_temperature = db.Column(db.Float, nullable=False)
    is_cooling = db.Column(db.Boolean, default=True)  # True for cooling, False for heating
    is_active = db.Column(db.Boolean, default=True)
    
    # For manual schedules
    start_time = db.Column(db.DateTime, nullable=True)  # For MANUAL type
    end_time = db.Column(db.DateTime, nullable=True)    # For MANUAL type
    
    # Relationships
    thermostat = db.relationship('Thermostat', back_populates='schedules')
    
    def to_dict(self):
        """Convert schedule to dictionary"""
        return {
            'id': self.id,
            'thermostat_id': self.thermostat_id,
            'schedule_type': self.schedule_type.value,
            'hours_before_checkin': self.hours_before_checkin,
            'hours_after_checkout': self.hours_after_checkout,
            'target_temperature': self.target_temperature,
            'is_cooling': self.is_cooling,
            'is_active': self.is_active,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
