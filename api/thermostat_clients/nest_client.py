import requests
import json
from datetime import datetime, timedelta
from .base_client import BaseThermostatClient

class NestClient(BaseThermostatClient):
    """Client for Google Nest thermostat API"""
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, project_id=None, access_token=None, refresh_token=None):
        """
        Initialize the Nest client
        
        Args:
            client_id (str): Google OAuth client ID
            client_secret (str): Google OAuth client secret
            redirect_uri (str): OAuth redirect URI
            project_id (str): Google project ID for the Device Access project
            access_token (str, optional): Existing access token
            refresh_token (str, optional): Existing refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.project_id = project_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = None
        self.base_url = "https://smartdevicemanagement.googleapis.com/v1"
    
    def authenticate(self, auth_code=None):
        """
        Authenticate with Google OAuth 2.0
        
        Args:
            auth_code (str, optional): Authorization code from OAuth flow
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        # If we have a valid access token, use it
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return True
            
        # If we have a refresh token, use it to get a new access token
        if self.refresh_token:
            return self._refresh_access_token()
            
        # If we have an auth code, exchange it for tokens
        if auth_code:
            return self._exchange_auth_code(auth_code)
            
        # No authentication method available
        return False
    
    def _exchange_auth_code(self, auth_code):
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            auth_code (str): Authorization code from OAuth flow
            
        Returns:
            bool: True if successful, False otherwise
        """
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                return bool(self.access_token)
        except Exception as e:
            print(f"Error exchanging auth code: {str(e)}")
        
        return False
    
    def _refresh_access_token(self):
        """
        Refresh access token using refresh token
        
        Returns:
            bool: True if successful, False otherwise
        """
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(token_url, data=payload)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                return bool(self.access_token)
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
        
        return False
    
    def get_status(self, device_id):
        """
        Get current status of the Nest thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Status information or None if failed
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        url = f"{self.base_url}/enterprises/{self.project_id}/devices/{device_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information from the Nest API response
                traits = data.get("traits", {})
                
                # Get temperature information
                temperature_trait = traits.get("sdm.devices.traits.Temperature", {})
                ambient_temp_c = temperature_trait.get("ambientTemperatureCelsius")
                
                # Get thermostat mode
                thermostat_mode_trait = traits.get("sdm.devices.traits.ThermostatMode", {})
                mode = thermostat_mode_trait.get("mode", "HEAT")
                
                # Get target temperature
                thermostat_setpoint_trait = traits.get("sdm.devices.traits.ThermostatTemperatureSetpoint", {})
                target_temp_c = None
                
                if mode == "HEAT":
                    target_temp_c = thermostat_setpoint_trait.get("heatCelsius")
                elif mode == "COOL":
                    target_temp_c = thermostat_setpoint_trait.get("coolCelsius")
                elif mode == "HEATCOOL":
                    target_temp_c = (
                        thermostat_setpoint_trait.get("heatCelsius", 0) +
                        thermostat_setpoint_trait.get("coolCelsius", 0)
                    ) / 2
                
                # Get fan status
                fan_trait = traits.get("sdm.devices.traits.Fan", {})
                fan_timer_mode = fan_trait.get("timerMode", "OFF")
                
                # Convert to our standardized format
                status = {
                    "temperature": self._celsius_to_fahrenheit(ambient_temp_c) if ambient_temp_c else None,
                    "target_temperature": self._celsius_to_fahrenheit(target_temp_c) if target_temp_c else None,
                    "mode": self._map_nest_mode_to_standard(mode),
                    "fan_mode": "on" if fan_timer_mode == "ON" else "auto",
                    "is_online": True,
                    "humidity": traits.get("sdm.devices.traits.Humidity", {}).get("ambientHumidityPercent"),
                    "raw_data": data  # Include raw data for debugging
                }
                
                return status
        except Exception as e:
            print(f"Error getting thermostat status: {str(e)}")
        
        return None
    
    def set_temperature(self, device_id, temperature):
        """
        Set target temperature for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            temperature (float): Target temperature in Fahrenheit
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        # First get current status to determine the mode
        status = self.get_status(device_id)
        if not status:
            return False
        
        mode = status.get("mode", "heat")
        temp_celsius = self._fahrenheit_to_celsius(temperature)
        
        url = f"{self.base_url}/enterprises/{self.project_id}/devices/{device_id}:executeCommand"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Command depends on the current mode
            if mode == "heat":
                payload = {
                    "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
                    "params": {
                        "heatCelsius": temp_celsius
                    }
                }
            elif mode == "cool":
                payload = {
                    "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool",
                    "params": {
                        "coolCelsius": temp_celsius
                    }
                }
            elif mode == "auto":
                # For auto mode, we need to set both heat and cool points
                # Typically with a reasonable range (e.g., ±2°F)
                heat_celsius = temp_celsius - 1.1  # About 2°F lower
                cool_celsius = temp_celsius + 1.1  # About 2°F higher
                
                payload = {
                    "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetRange",
                    "params": {
                        "heatCelsius": heat_celsius,
                        "coolCelsius": cool_celsius
                    }
                }
            else:
                # Cannot set temperature in OFF mode
                return False
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting temperature: {str(e)}")
        
        return False
    
    def set_mode(self, device_id, mode):
        """
        Set thermostat mode (heat, cool, off, etc.)
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            mode (str): Operating mode (heat, cool, auto, off)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        # Map our standard modes to Nest API modes
        nest_mode = self._map_standard_mode_to_nest(mode)
        
        url = f"{self.base_url}/enterprises/{self.project_id}/devices/{device_id}:executeCommand"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            payload = {
                "command": "sdm.devices.commands.ThermostatMode.SetMode",
                "params": {
                    "mode": nest_mode
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting mode: {str(e)}")
        
        return False
    
    def set_fan_mode(self, device_id, fan_mode):
        """
        Set fan mode (auto, on)
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            fan_mode (str): Fan mode (auto, on)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        # Map our standard fan modes to Nest API fan modes
        timer_mode = "ON" if fan_mode.lower() == "on" else "OFF"
        
        url = f"{self.base_url}/enterprises/{self.project_id}/devices/{device_id}:executeCommand"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # For Nest, we use the Fan Timer feature to control the fan
            # When ON, set a duration (e.g., 1 hour)
            # When OFF, set duration to 0
            payload = {
                "command": "sdm.devices.commands.Fan.SetTimer",
                "params": {
                    "timerMode": timer_mode,
                    "duration": "3600s" if timer_mode == "ON" else "0s"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting fan mode: {str(e)}")
        
        return False
    
    def get_schedule(self, device_id):
        """
        Get current schedule for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Schedule information or None if not supported/failed
        """
        # Nest doesn't have a direct schedule API through the Device Access API
        # This would need to be implemented through Google Home routines or a custom solution
        return None
    
    def set_schedule(self, device_id, schedule):
        """
        Set schedule for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            schedule (dict): Schedule information in a standardized format
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Nest doesn't have a direct schedule API through the Device Access API
        # This would need to be implemented through Google Home routines or a custom solution
        return False
    
    def _fahrenheit_to_celsius(self, fahrenheit):
        """
        Convert Fahrenheit to Celsius
        
        Args:
            fahrenheit (float): Temperature in Fahrenheit
            
        Returns:
            float: Temperature in Celsius
        """
        return (fahrenheit - 32) * 5 / 9
    
    def _celsius_to_fahrenheit(self, celsius):
        """
        Convert Celsius to Fahrenheit
        
        Args:
            celsius (float): Temperature in Celsius
            
        Returns:
            float: Temperature in Fahrenheit
        """
        return (celsius * 9 / 5) + 32
    
    def _map_nest_mode_to_standard(self, nest_mode):
        """
        Map Nest API mode to our standard mode
        
        Args:
            nest_mode (str): Nest API mode
            
        Returns:
            str: Standard mode (heat, cool, auto, off)
        """
        mode_map = {
            "HEAT": "heat",
            "COOL": "cool",
            "HEATCOOL": "auto",
            "OFF": "off"
        }
        return mode_map.get(nest_mode, "heat")
    
    def _map_standard_mode_to_nest(self, mode):
        """
        Map our standard mode to Nest API mode
        
        Args:
            mode (str): Standard mode (heat, cool, auto, off)
            
        Returns:
            str: Nest API mode
        """
        mode_map = {
            "heat": "HEAT",
            "cool": "COOL",
            "auto": "HEATCOOL",
            "off": "OFF"
        }
        return mode_map.get(mode.lower(), "HEAT")
