from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    """
    Property model representing a physical location with thermostats
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.address}, {self.city}"

    class Meta:
        verbose_name_plural = "Properties"


class Thermostat(models.Model):
    """
    Thermostat model representing a physical thermostat device
    """
    THERMOSTAT_TYPES = (
        ('NEST', 'Nest'),
        ('CIELO', 'Cielo'),
        ('PIONEER', 'Pioneer'),
    )
    
    name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=THERMOSTAT_TYPES)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='thermostats')
    is_online = models.BooleanField(default=False)
    last_temperature = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    api_key = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - {self.property.name}"


class Calendar(models.Model):
    """
    Calendar model for integrating with external calendars
    """
    CALENDAR_TYPES = (
        ('GOOGLE', 'Google Calendar'),
        ('ICAL', 'iCalendar'),
        ('BOOKING', 'Booking System'),
        ('MANUAL', 'Manual Calendar'),
    )
    
    SYNC_FREQUENCIES = (
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('MANUAL', 'Manual'),
    )
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=CALENDAR_TYPES)
    url = models.URLField(null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='calendars')
    sync_frequency = models.CharField(max_length=20, choices=SYNC_FREQUENCIES)
    credentials = models.TextField(null=True, blank=True)  # Encrypted in production
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - {self.property.name}"

    class Meta:
        verbose_name_plural = "Calendars"


class Schedule(models.Model):
    """
    Schedule model for thermostat temperature scheduling
    """
    SCHEDULE_TYPES = (
        ('BOOKING', 'Booking-based'),
        ('TIME', 'Time-based'),
        ('OCCUPANCY', 'Occupancy-based'),
    )
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    thermostat = models.ForeignKey(Thermostat, on_delete=models.CASCADE, related_name='schedules')
    occupied_temp = models.FloatField()
    unoccupied_temp = models.FloatField()
    pre_arrival_hours = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.thermostat.name}"


class TemperatureLog(models.Model):
    """
    Temperature log for tracking thermostat temperature changes
    """
    thermostat = models.ForeignKey(Thermostat, on_delete=models.CASCADE, related_name='temperature_logs')
    temperature = models.FloatField()
    is_occupied = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.thermostat.name} - {self.temperature}°F at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


class UserProfile(models.Model):
    """
    Extended user profile for additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, default='manager')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
