from src.models.base import db, BaseModel
from src.models.calendar import Calendar
from datetime import datetime

class Booking(db.Model, BaseModel):
    """Booking model for storing guest booking information"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    guest_name = db.Column(db.String(255), nullable=True)
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    booking_reference = db.Column(db.String(255), nullable=True)  # External reference ID
    source = db.Column(db.String(50), nullable=True)  # 'airbnb', 'vrbo', etc.
    
    # Relationships
    calendar = db.relationship('Calendar', back_populates='bookings')
    
    def to_dict(self):
        """Convert booking to dictionary"""
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'guest_name': self.guest_name,
            'check_in': self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'booking_reference': self.booking_reference,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @property
    def is_active(self):
        """Check if booking is currently active"""
        now = datetime.utcnow()
        return self.check_in <= now <= self.check_out
