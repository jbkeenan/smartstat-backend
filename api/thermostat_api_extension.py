from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import json

from .thermostat_clients.client_factory import ThermostatClientFactory

# Add these imports to the existing imports in views.py
def extend_thermostat_viewset(ThermostatViewSet):
    """
    Extend the ThermostatViewSet with additional actions for thermostat control
    This function should be called after the ThermostatViewSet class definition
    """
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get current status of the thermostat"""
        thermostat = self.get_object()
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                status_data = client.get_status(thermostat.device_id)
                if status_data:
                    # Update thermostat record with latest data
                    if 'temperature' in status_data:
                        thermostat.last_temperature = status_data['temperature']
                        thermostat.last_updated = timezone.now()
                        thermostat.is_online = True
                        thermostat.save()
                    
                    return Response(status_data)
                return Response({"error": "Failed to get thermostat status"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_temperature(self, request, pk=None):
        """Set target temperature for the thermostat"""
        thermostat = self.get_object()
        temperature = request.data.get('temperature')
        
        if not temperature:
            return Response({"error": "Temperature is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                success = client.set_temperature(thermostat.device_id, float(temperature))
                if success:
                    return Response({"success": True})
                return Response({"error": "Failed to set temperature"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_mode(self, request, pk=None):
        """Set thermostat mode (heat, cool, off, etc.)"""
        thermostat = self.get_object()
        mode = request.data.get('mode')
        
        if not mode:
            return Response({"error": "Mode is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                success = client.set_mode(thermostat.device_id, mode)
                if success:
                    return Response({"success": True})
                return Response({"error": "Failed to set mode"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_fan_mode(self, request, pk=None):
        """Set fan mode (auto, on)"""
        thermostat = self.get_object()
        fan_mode = request.data.get('fan_mode')
        
        if not fan_mode:
            return Response({"error": "Fan mode is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                success = client.set_fan_mode(thermostat.device_id, fan_mode)
                if success:
                    return Response({"success": True})
                return Response({"error": "Failed to set fan mode"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get current schedule for the thermostat"""
        thermostat = self.get_object()
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                schedule_data = client.get_schedule(thermostat.device_id)
                if schedule_data:
                    return Response(schedule_data)
                return Response({"error": "Failed to get schedule or not supported"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def set_schedule(self, request, pk=None):
        """Set schedule for the thermostat"""
        thermostat = self.get_object()
        schedule = request.data
        
        if not schedule:
            return Response({"error": "Schedule data is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = ThermostatClientFactory.create_client(
                thermostat_type=thermostat.type,
                **self._get_client_kwargs(thermostat)
            )
            
            if client.authenticate():
                success = client.set_schedule(thermostat.device_id, schedule)
                if success:
                    return Response({"success": True})
                return Response({"error": "Failed to set schedule or not supported"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_kwargs(self, thermostat):
        """Get kwargs for client initialization based on thermostat type"""
        from django.conf import settings
        
        # Try to parse API key as JSON if it exists
        credentials = {}
        if thermostat.api_key:
            try:
                credentials = json.loads(thermostat.api_key)
            except json.JSONDecodeError:
                # If not valid JSON, use as-is
                credentials = {"token": thermostat.api_key}
        
        if thermostat.type == "NEST":
            return {
                "client_id": getattr(settings, "NEST_CLIENT_ID", credentials.get("client_id")),
                "client_secret": getattr(settings, "NEST_CLIENT_SECRET", credentials.get("client_secret")),
                "redirect_uri": getattr(settings, "NEST_REDIRECT_URI", credentials.get("redirect_uri")),
                "project_id": getattr(settings, "NEST_PROJECT_ID", credentials.get("project_id")),
                "access_token": credentials.get("access_token"),
                "refresh_token": credentials.get("refresh_token")
            }
        elif thermostat.type == "CIELO":
            return {
                "username": credentials.get("username"),
                "password": credentials.get("password"),
                "token": credentials.get("token")
            }
        elif thermostat.type == "PIONEER":
            return {
                "username": credentials.get("username"),
                "password": credentials.get("password"),
                "device_key": credentials.get("device_key")
            }
        return {}
    
    # Add the methods to the ThermostatViewSet class
    setattr(ThermostatViewSet, 'status', status)
    setattr(ThermostatViewSet, 'set_temperature', set_temperature)
    setattr(ThermostatViewSet, 'set_mode', set_mode)
    setattr(ThermostatViewSet, 'set_fan_mode', set_fan_mode)
    setattr(ThermostatViewSet, 'schedule', schedule)
    setattr(ThermostatViewSet, 'set_schedule', set_schedule)
    setattr(ThermostatViewSet, '_get_client_kwargs', _get_client_kwargs)
    
    return ThermostatViewSet
