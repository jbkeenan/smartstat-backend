import pytest
from src.models.user import User, UserRole
from src.models.property import Property
from src.models.thermostat import Thermostat, ThermostatType
from src.models.calendar import Calendar
from src.models.booking import Booking
from src.models.schedule import Schedule, ScheduleType
from src.models.thermostat_log import ThermostatLog, LogType
from datetime import datetime, timedelta

# Test data
test_user = {
    'email': 'test@example.com',
    'password': 'password123',
    'first_name': 'Test',
    'last_name': 'User'
}

test_property = {
    'name': 'Test Property',
    'address': '123 Main St',
    'city': 'Testville',
    'state': 'TS',
    'zip_code': '12345',
    'country': 'Testland'
}

test_thermostat = {
    'name': 'Living Room',
    'device_id': 'TEST123',
    'type': ThermostatType.NEST
}

test_calendar = {
    'name': 'Airbnb Calendar',
    'source_type': 'ical',
    'source_url': 'https://example.com/calendar.ics'
}

test_booking = {
    'guest_name': 'John Doe',
    'check_in': datetime.utcnow() + timedelta(days=1),
    'check_out': datetime.utcnow() + timedelta(days=3),
    'booking_reference': 'TEST123',
    'source': 'airbnb'
}

test_schedule = {
    'schedule_type': ScheduleType.CHECK_IN,
    'hours_before_checkin': 3,
    'target_temperature': 72.0,
    'is_cooling': True
}

@pytest.fixture
def app():
    from src.main import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        from src.models.base import db
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    from src.models.base import db
    with app.app_context():
        yield db.session

def test_user_model(db_session):
    """Test User model creation and password hashing"""
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name'],
        role=UserRole.MANAGER
    )
    user.set_password(test_user['password'])
    db_session.add(user)
    db_session.commit()
    
    saved_user = User.query.filter_by(email=test_user['email']).first()
    assert saved_user is not None
    assert saved_user.email == test_user['email']
    assert saved_user.check_password(test_user['password'])
    assert not saved_user.check_password('wrong_password')

def test_property_model(db_session):
    """Test Property model creation and relationships"""
    # Create user first
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name']
    )
    user.set_password(test_user['password'])  # Fix: Set password
    db_session.add(user)
    db_session.commit()
    
    # Create property
    property = Property(
        name=test_property['name'],
        address=test_property['address'],
        city=test_property['city'],
        state=test_property['state'],
        zip_code=test_property['zip_code'],
        country=test_property['country'],
        user_id=user.id
    )
    db_session.add(property)
    db_session.commit()
    
    saved_property = Property.query.filter_by(name=test_property['name']).first()
    assert saved_property is not None
    assert saved_property.name == test_property['name']
    assert saved_property.user_id == user.id
    assert saved_property.user.email == user.email

def test_thermostat_model(db_session):
    """Test Thermostat model creation and relationships"""
    # Create user and property first
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name']
    )
    user.set_password(test_user['password'])  # Fix: Set password
    db_session.add(user)
    db_session.commit()
    
    property = Property(
        name=test_property['name'],
        address=test_property['address'],
        city=test_property['city'],
        state=test_property['state'],
        zip_code=test_property['zip_code'],
        country=test_property['country'],
        user_id=user.id
    )
    db_session.add(property)
    db_session.commit()
    
    # Create thermostat
    thermostat = Thermostat(
        name=test_thermostat['name'],
        device_id=test_thermostat['device_id'],
        type=test_thermostat['type'],
        property_id=property.id
    )
    db_session.add(thermostat)
    db_session.commit()
    
    saved_thermostat = Thermostat.query.filter_by(name=test_thermostat['name']).first()
    assert saved_thermostat is not None
    assert saved_thermostat.name == test_thermostat['name']
    assert saved_thermostat.type == test_thermostat['type']
    assert saved_thermostat.property_id == property.id
    assert saved_thermostat.property.name == property.name

def test_calendar_and_booking_models(db_session):
    """Test Calendar and Booking models creation and relationships"""
    # Create user and property first
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name']
    )
    user.set_password(test_user['password'])  # Fix: Set password
    db_session.add(user)
    db_session.commit()
    
    property = Property(
        name=test_property['name'],
        address=test_property['address'],
        city=test_property['city'],
        state=test_property['state'],
        zip_code=test_property['zip_code'],
        country=test_property['country'],
        user_id=user.id
    )
    db_session.add(property)
    db_session.commit()
    
    # Create calendar
    calendar = Calendar(
        name=test_calendar['name'],
        source_type=test_calendar['source_type'],
        source_url=test_calendar['source_url'],
        property_id=property.id
    )
    db_session.add(calendar)
    db_session.commit()
    
    # Create booking
    booking = Booking(
        calendar_id=calendar.id,
        guest_name=test_booking['guest_name'],
        check_in=test_booking['check_in'],
        check_out=test_booking['check_out'],
        booking_reference=test_booking['booking_reference'],
        source=test_booking['source']
    )
    db_session.add(booking)
    db_session.commit()
    
    saved_calendar = Calendar.query.filter_by(name=test_calendar['name']).first()
    assert saved_calendar is not None
    assert saved_calendar.name == test_calendar['name']
    assert saved_calendar.property_id == property.id
    
    saved_booking = Booking.query.filter_by(booking_reference=test_booking['booking_reference']).first()
    assert saved_booking is not None
    assert saved_booking.guest_name == test_booking['guest_name']
    assert saved_booking.calendar_id == calendar.id
    assert saved_booking.calendar.name == calendar.name

def test_schedule_model(db_session):
    """Test Schedule model creation and relationships"""
    # Create user, property, and thermostat first
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name']
    )
    user.set_password(test_user['password'])  # Fix: Set password
    db_session.add(user)
    db_session.commit()
    
    property = Property(
        name=test_property['name'],
        address=test_property['address'],
        city=test_property['city'],
        state=test_property['state'],
        zip_code=test_property['zip_code'],
        country=test_property['country'],
        user_id=user.id
    )
    db_session.add(property)
    db_session.commit()
    
    thermostat = Thermostat(
        name=test_thermostat['name'],
        device_id=test_thermostat['device_id'],
        type=test_thermostat['type'],
        property_id=property.id
    )
    db_session.add(thermostat)
    db_session.commit()
    
    # Create schedule
    schedule = Schedule(
        thermostat_id=thermostat.id,
        schedule_type=test_schedule['schedule_type'],
        hours_before_checkin=test_schedule['hours_before_checkin'],
        target_temperature=test_schedule['target_temperature'],
        is_cooling=test_schedule['is_cooling']
    )
    db_session.add(schedule)
    db_session.commit()
    
    saved_schedule = Schedule.query.filter_by(thermostat_id=thermostat.id).first()
    assert saved_schedule is not None
    assert saved_schedule.schedule_type == test_schedule['schedule_type']
    assert saved_schedule.target_temperature == test_schedule['target_temperature']
    assert saved_schedule.thermostat_id == thermostat.id
    assert saved_schedule.thermostat.name == thermostat.name

def test_thermostat_log_model(db_session):
    """Test ThermostatLog model creation and relationships"""
    # Create user, property, and thermostat first
    user = User(
        email=test_user['email'],
        first_name=test_user['first_name'],
        last_name=test_user['last_name']
    )
    user.set_password(test_user['password'])  # Fix: Set password
    db_session.add(user)
    db_session.commit()
    
    property = Property(
        name=test_property['name'],
        address=test_property['address'],
        city=test_property['city'],
        state=test_property['state'],
        zip_code=test_property['zip_code'],
        country=test_property['country'],
        user_id=user.id
    )
    db_session.add(property)
    db_session.commit()
    
    thermostat = Thermostat(
        name=test_thermostat['name'],
        device_id=test_thermostat['device_id'],
        type=test_thermostat['type'],
        property_id=property.id
    )
    db_session.add(thermostat)
    db_session.commit()
    
    # Create log
    log = ThermostatLog(
        thermostat_id=thermostat.id,
        log_type=LogType.INFO,
        message="Test log message"
    )
    db_session.add(log)
    db_session.commit()
    
    saved_log = ThermostatLog.query.filter_by(thermostat_id=thermostat.id).first()
    assert saved_log is not None
    assert saved_log.log_type == LogType.INFO
    assert saved_log.message == "Test log message"
    assert saved_log.thermostat_id == thermostat.id
    assert saved_log.thermostat.name == thermostat.name
