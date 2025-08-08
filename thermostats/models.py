from django.db import models
from django.conf import settings

class Property(models.Model):
    """Model for properties that have thermostats"""
    PROPERTY_TYPES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('vacation', 'Vacation Rental'),
    ]
    
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    size = models.IntegerField(help_text="Size in square feet")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Address fields
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')

    # Timezone of the property.  Each property can live in a different timezone,
    # which is important for scheduling pre‑arrival and post‑checkout actions.
    # Defaults to America/Chicago (UTC−06:00/UTC−05:00 in DST) but can be
    # overridden by the user.  See tz database names for valid values.
    timezone = models.CharField(
        max_length=50,
        default='America/Chicago',
        help_text='Timezone of the property, e.g. America/Chicago'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Properties"


class Thermostat(models.Model):
    """Model for thermostats associated with properties"""
    THERMOSTAT_BRANDS = [
        ('nest', 'Google Nest'),
        ('cielo', 'Cielo'),
        ('pioneer', 'Pioneer'),
        ('other', 'Other'),
    ]
    
    THERMOSTAT_MODES = [
        ('heat', 'Heat'),
        ('cool', 'Cool'),
        ('auto', 'Auto'),
        ('off', 'Off'),
    ]
    
    name = models.CharField(max_length=100)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='thermostats')
    brand = models.CharField(max_length=20, choices=THERMOSTAT_BRANDS)
    model = models.CharField(max_length=100)
    device_id = models.CharField(max_length=255, unique=True)
    current_temperature = models.FloatField(null=True, blank=True)
    target_temperature = models.FloatField(null=True, blank=True)
    current_humidity = models.FloatField(null=True, blank=True)
    mode = models.CharField(max_length=10, choices=THERMOSTAT_MODES, default='off')
    is_online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # API credentials (encrypted in production)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_token = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_brand_display()})"


class CalendarEvent(models.Model):
    """Model for calendar events associated with properties"""
    EVENT_TYPES = [
        ('booking', 'Booking'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # External calendar sync info
    external_id = models.CharField(max_length=255, blank=True, null=True)
    external_calendar_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%Y-%m-%d')})"


class ThermostatCommand(models.Model):
    """Model for tracking commands sent to thermostats"""
    COMMAND_TYPES = [
        ('set_temperature', 'Set Temperature'),
        ('set_mode', 'Set Mode'),
        ('set_schedule', 'Set Schedule'),
        ('other', 'Other'),
    ]
    
    COMMAND_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    thermostat = models.ForeignKey(Thermostat, on_delete=models.CASCADE, related_name='commands')
    command_type = models.CharField(max_length=20, choices=COMMAND_TYPES)
    parameters = models.JSONField()
    status = models.CharField(max_length=10, choices=COMMAND_STATUS, default='pending')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_command_type_display()} to {self.thermostat.name}"


class UsageStatistics(models.Model):
    """Model for tracking energy usage and savings"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='statistics')
    date = models.DateField()
    energy_usage = models.FloatField(help_text="Energy usage in kWh")
    cost = models.FloatField(help_text="Cost in USD")
    savings = models.FloatField(help_text="Estimated savings in USD", null=True, blank=True)
    average_temperature = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Statistics for {self.property.name} on {self.date}"
    
    class Meta:
        verbose_name_plural = "Usage statistics"
