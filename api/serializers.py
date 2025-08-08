from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Property, Thermostat, Calendar, Schedule, TemperatureLog, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for the UserProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'phone', 'company', 'role', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for the Property model"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Property
        fields = ('id', 'name', 'address', 'city', 'state', 'zip_code', 'country', 
                  'user', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ThermostatSerializer(serializers.ModelSerializer):
    """Serializer for the Thermostat model"""
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    
    class Meta:
        model = Thermostat
        fields = ('id', 'name', 'device_id', 'type', 'property', 'is_online', 
                  'last_temperature', 'last_updated', 'api_key', 'ip_address', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'is_online', 'last_temperature', 'last_updated', 
                           'created_at', 'updated_at')


class CalendarSerializer(serializers.ModelSerializer):
    """Serializer for the Calendar model"""
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    
    class Meta:
        model = Calendar
        fields = ('id', 'name', 'type', 'url', 'property', 'sync_frequency', 
                  'credentials', 'last_synced', 'created_at', 'updated_at')
        read_only_fields = ('id', 'last_synced', 'created_at', 'updated_at')


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for the Schedule model"""
    thermostat = serializers.PrimaryKeyRelatedField(queryset=Thermostat.objects.all())
    
    class Meta:
        model = Schedule
        fields = ('id', 'name', 'type', 'thermostat', 'occupied_temp', 
                  'unoccupied_temp', 'pre_arrival_hours', 'is_active', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TemperatureLogSerializer(serializers.ModelSerializer):
    """Serializer for the TemperatureLog model"""
    thermostat = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = TemperatureLog
        fields = ('id', 'thermostat', 'temperature', 'is_occupied', 'timestamp')
        read_only_fields = ('id', 'timestamp')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
