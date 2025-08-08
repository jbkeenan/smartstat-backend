from rest_framework import serializers
from .models import Property, Thermostat, CalendarEvent, ThermostatCommand, UsageStatistics

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'type', 'size', 'street', 'city', 'state', 'zip_code', 'country', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Automatically assign the current user as the owner
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class ThermostatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thermostat
        fields = ['id', 'name', 'property', 'brand', 'model', 'device_id', 'current_temperature', 
                 'target_temperature', 'current_humidity', 'mode', 'is_online', 'created_at', 'updated_at']
        read_only_fields = ['id', 'current_temperature', 'current_humidity', 'is_online', 'created_at', 'updated_at']

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ['id', 'property', 'title', 'description', 'start_date', 'end_date', 
                 'event_type', 'external_id', 'external_calendar_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ThermostatCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThermostatCommand
        fields = ['id', 'thermostat', 'command_type', 'parameters', 'status', 'result', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'result', 'created_at', 'updated_at']

class UsageStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageStatistics
        fields = ['id', 'property', 'date', 'energy_usage', 'cost', 'savings', 'average_temperature']
        read_only_fields = ['id']
