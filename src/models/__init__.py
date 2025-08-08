from src.models.user import User
from src.models.property import Property
from src.models.thermostat import Thermostat, ThermostatType
from src.models.calendar import Calendar
from src.models.booking import Booking
from src.models.schedule import Schedule, ScheduleType
from src.models.thermostat_log import ThermostatLog, LogType

# Import all models here for easy access
__all__ = [
    'User', 
    'Property', 
    'Thermostat', 
    'ThermostatType',
    'Calendar', 
    'Booking', 
    'Schedule', 
    'ScheduleType',
    'ThermostatLog', 
    'LogType'
]
