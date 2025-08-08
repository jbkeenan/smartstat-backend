from django.db import models
from django.conf import settings


class Property(models.Model):
    """
    Model representing a physical property with a thermostat.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Property settings
    square_footage = models.PositiveIntegerField(null=True, blank=True)
    num_bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    num_bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    property_type = models.CharField(
        max_length=50,
        choices=[
            ('house', 'House'),
            ('apartment', 'Apartment'),
            ('condo', 'Condominium'),
            ('cabin', 'Cabin'),
            ('other', 'Other')
        ],
        default='house'
    )
    
    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class PropertySettings(models.Model):
    """
    Model for property-specific settings.
    """
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    
    # Temperature settings
    default_temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=22.0
    )
    away_temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=18.0
    )
    
    # Energy saving settings
    energy_saving_mode = models.BooleanField(default=False)
    schedule_enabled = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Property Settings'
        verbose_name_plural = 'Property Settings'
    
    def __str__(self):
        return f"Settings for {self.property.name}"
