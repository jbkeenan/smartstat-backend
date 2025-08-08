from rest_framework import serializers
from .models import Property, PropertySettings


class PropertySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertySettings
        fields = [
            'id', 'default_temperature', 'away_temperature',
            'energy_saving_mode', 'schedule_enabled'
        ]


class PropertySerializer(serializers.ModelSerializer):
    settings = PropertySettingsSerializer(read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'name', 'address', 'owner', 'created_at', 'updated_at',
            'square_footage', 'num_bedrooms', 'num_bathrooms', 
            'property_type', 'settings'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Ensure the current user is set as the owner
        user = self.context['request'].user
        property_instance = Property.objects.create(
            owner=user,
            **validated_data
        )
        
        # Create default settings for the property
        PropertySettings.objects.create(property=property_instance)
        
        return property_instance
