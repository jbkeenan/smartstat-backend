import requests
import json
from datetime import datetime, timedelta
from .base_client import BaseThermostatClient

class PioneerClient(BaseThermostatClient):
    """Client for Pioneer thermostat API"""
    
    def __init__(self, username=None, password=None, device_key=None):
        """
        Initialize the Pioneer client
        
        Args:
            username (str, optional): Pioneer account username
            password (str, optional): Pioneer account password
            device_key (str, optional): Device-specific API key
        """
        self.username = username
        self.password = password
        self.device_key = device_key
        self.token = None
        self.token_expiry = None
        self.base_url = "https://api.pioneerminisplit.com/api"  # Example URL, may need to be updated
    
    def authenticate(self):
        """
        Authenticate with Pioneer API
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        # If we have a valid token, use it
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return True
        
        # If we have a device key, use that for authentication
        if self.device_key:
            self.token = self.device_key
            self.token_expiry = datetime.now() + timedelta(days=30)  # Assume long validity
            return True
        
        # Otherwise, authenticate with username and password
        if not self.username or not self.password:
            return False
        
        auth_url = f"{self.base_url}/auth"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(auth_url, json=payload)
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("token")
                # Typically tokens are valid for a certain period
                expires_in = auth_data.get("expires_in", 86400)  # Default to 24 hours
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                return bool(self.token)
        except Exception as e:
            print(f"Error authenticating with Pioneer API: {str(e)}")
        
        return False
    
    def get_status(self, device_id):
        """
        Get current status of the Pioneer thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Status information or None if failed
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        url = f"{self.base_url}/devices/{device_id}/status"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information from the Pioneer API response
                # Note: This is based on community documentation and may need adjustment
                status = {
                    "temperature": data.get("current_temperature"),
                    "target_temperature": data.get("target_temperature"),
                    "mode": data.get("mode", "heat").lower(),
                    "fan_mode": data.get("fan_mode", "auto").lower(),
                    "is_online": data.get("is_online", True),
                    "humidity": data.get("humidity"),
                    "raw_data": data  # Include raw data for debugging
                }
                
                return status
        except Exception as e:
            print(f"Error getting Pioneer thermostat status: {str(e)}")
        
        return None
    
    def set_temperature(self, device_id, temperature):
        """
        Set target temperature for the Pioneer thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            temperature (float): Target temperature in Fahrenheit
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        url = f"{self.base_url}/devices/{device_id}/temperature"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"temperature": temperature}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting Pioneer temperature: {str(e)}")
        
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
        
        # Map standard modes to Pioneer-specific modes if needed
        pioneer_mode = self._map_standard_mode_to_pioneer(mode)
        
        url = f"{self.base_url}/devices/{device_id}/mode"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"mode": pioneer_mode}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting Pioneer mode: {str(e)}")
        
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
        
        # Map standard fan modes to Pioneer-specific fan modes if needed
        pioneer_fan_mode = fan_mode.lower()
        
        url = f"{self.base_url}/devices/{device_id}/fan"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"fan_mode": pioneer_fan_mode}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting Pioneer fan mode: {str(e)}")
        
        return False
    
    def get_schedule(self, device_id):
        """
        Get current schedule for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Schedule information or None if not supported/failed
        """
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        url = f"{self.base_url}/devices/{device_id}/schedule"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting Pioneer schedule: {str(e)}")
        
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
        if not self.authenticate():
            raise Exception("Not authenticated")
        
        url = f"{self.base_url}/devices/{device_id}/schedule"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=schedule)
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting Pioneer schedule: {str(e)}")
        
        return False
    
    def _map_standard_mode_to_pioneer(self, mode):
        """
        Map standard mode to Pioneer-specific mode if needed
        
        Args:
            mode (str): Standard mode (heat, cool, auto, off)
            
        Returns:
            str: Pioneer-specific mode
        """
        # For now, assume Pioneer uses the same mode names
        # This can be updated if Pioneer uses different terminology
        return mode.lower()
