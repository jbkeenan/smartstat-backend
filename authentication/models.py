from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extended user model with additional fields"""
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    preferred_temperature_unit = models.CharField(
        max_length=1,
        choices=[('F', 'Fahrenheit'), ('C', 'Celsius')],
        default='F'
    )
    
    def __str__(self):
        return self.email
