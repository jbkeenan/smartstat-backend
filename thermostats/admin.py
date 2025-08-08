from django.contrib import admin
from .models import Property, Thermostat, CalendarEvent, ThermostatCommand, UsageStatistics

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'type', 'city', 'state', 'created_at')
    list_filter = ('type', 'state')
    search_fields = ('name', 'owner__email', 'city', 'state')

@admin.register(Thermostat)
class ThermostatAdmin(admin.ModelAdmin):
    list_display = ('name', 'property', 'brand', 'model', 'current_temperature', 'mode', 'is_online')
    list_filter = ('brand', 'mode', 'is_online')
    search_fields = ('name', 'property__name', 'device_id')

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'property', 'event_type', 'start_date', 'end_date')
    list_filter = ('event_type',)
    search_fields = ('title', 'property__name', 'description')

@admin.register(ThermostatCommand)
class ThermostatCommandAdmin(admin.ModelAdmin):
    list_display = ('thermostat', 'command_type', 'status', 'created_at')
    list_filter = ('command_type', 'status')
    search_fields = ('thermostat__name',)

@admin.register(UsageStatistics)
class UsageStatisticsAdmin(admin.ModelAdmin):
    list_display = ('property', 'date', 'energy_usage', 'cost', 'savings')
    list_filter = ('date',)
    search_fields = ('property__name',)
