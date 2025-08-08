from django.contrib import admin
from .models import Property, PropertySettings


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'owner', 'property_type', 'created_at')
    list_filter = ('property_type', 'created_at')
    search_fields = ('name', 'address', 'owner__username')
    date_hierarchy = 'created_at'


@admin.register(PropertySettings)
class PropertySettingsAdmin(admin.ModelAdmin):
    list_display = ('property', 'default_temperature', 'away_temperature', 'energy_saving_mode')
    list_filter = ('energy_saving_mode', 'schedule_enabled')
    search_fields = ('property__name',)
