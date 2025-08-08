from django.contrib import admin
from .models import Property, Thermostat, Calendar, Schedule, TemperatureLog, UserProfile

# Register models with the admin site
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'state', 'user')
    search_fields = ('name', 'address', 'city')
    list_filter = ('state', 'country')

@admin.register(Thermostat)
class ThermostatAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'type', 'property', 'is_online', 'last_temperature')
    search_fields = ('name', 'device_id')
    list_filter = ('type', 'is_online', 'property')

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'property', 'sync_frequency', 'last_synced')
    search_fields = ('name',)
    list_filter = ('type', 'sync_frequency')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'thermostat', 'occupied_temp', 'unoccupied_temp', 'is_active')
    search_fields = ('name',)
    list_filter = ('type', 'is_active')

@admin.register(TemperatureLog)
class TemperatureLogAdmin(admin.ModelAdmin):
    list_display = ('thermostat', 'temperature', 'is_occupied', 'timestamp')
    list_filter = ('is_occupied', 'timestamp')
    date_hierarchy = 'timestamp'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'role')
    search_fields = ('user__username', 'user__email', 'company')
    list_filter = ('role',)
