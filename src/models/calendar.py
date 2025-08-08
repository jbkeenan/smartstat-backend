from src.models.base import db, BaseModel
from src.models.property import Property

class Calendar(db.Model, BaseModel):
    """Calendar model for storing calendar information and booking sources"""
    __tablename__ = 'calendars'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)  # 'google', 'ical', etc.
    source_url = db.Column(db.String(1024), nullable=False)  # URL or identifier for the calendar
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    last_synced = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    property = db.relationship('Property', back_populates='calendars')
    bookings = db.relationship('Booking', back_populates='calendar', lazy='dynamic')
    
    def to_dict(self):
        """Convert calendar to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'source_url': self.source_url,
            'property_id': self.property_id,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
