"""
Thermostat adapter module for integrating with various thermostat brands.
This module implements the adapter pattern to provide a consistent interface
for different thermostat APIs (Google/Nest, Cielo, Pioneer).
"""

import abc
import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ThermostatAdapter(abc.ABC):
    """Abstract base class for thermostat adapters."""
    
    @abc.abstractmethod
    def get_temperature(self):
        """Get the current temperature from the thermostat."""
        pass
    
    @abc.abstractmethod
    def set_temperature(self, temperature):
        """Set the target temperature for the thermostat."""
        pass
    
    @abc.abstractmethod
    def get_humidity(self):
        """Get the current humidity from the thermostat."""
        pass
    
    @abc.abstractmethod
    def get_mode(self):
        """Get the current mode of the thermostat."""
        pass
    
    @abc.abstractmethod
    def set_mode(self, mode):
        """Set the mode of the thermostat."""
        pass
    
    @abc.abstractmethod
    def is_online(self):
        """Check if the thermostat is online."""
        pass
    
    def get_status(self):
        """Get the complete status of the thermostat."""
        return {
            'temperature': self.get_temperature(),
            'humidity': self.get_humidity(),
            'mode': self.get_mode(),
            'online': self.is_online()
        }
    
    def send_command(self, command_type, parameters):
        """Send a generic command to the thermostat."""
        if command_type == 'set_temperature':
            return self.set_temperature(parameters.get('temperature'))
        elif command_type == 'set_mode':
            return self.set_mode(parameters.get('mode'))
        else:
            logger.error(f"Unsupported command type: {command_type}")
            return False


class NestThermostatAdapter(ThermostatAdapter):
    """Adapter for Google Nest thermostats using the Smart Device Management API."""
    
    def __init__(self, device_id, api_key=None, api_token=None):
        self.device_id = device_id
        self.api_key = api_key or settings.NEST_API_KEY
        self.api_token = api_token or settings.NEST_API_TOKEN
        self.base_url = "https://smartdevicemanagement.googleapis.com/v1"
        
    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
    
    def _get_device_path(self):
        return f"enterprises/{self.api_key}/devices/{self.device_id}"
    
    def get_temperature(self):
        try:
            url = f"{self.base_url}/{self._get_device_path()}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("traits", {}).get("sdm.devices.traits.Temperature", {}).get("ambientTemperatureCelsius")
        except Exception as e:
            logger.error(f"Error getting temperature from Nest thermostat: {e}")
            return None
    
    def set_temperature(self, temperature):
        try:
            url = f"{self.base_url}/{self._get_device_path()}:executeCommand"
            payload = {
                "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat",
                "params": {
                    "heatCelsius": temperature
                }
            }
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error setting temperature for Nest thermostat: {e}")
            return False
    
    def get_humidity(self):
        try:
            url = f"{self.base_url}/{self._get_device_path()}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("traits", {}).get("sdm.devices.traits.Humidity", {}).get("ambientHumidityPercent")
        except Exception as e:
            logger.error(f"Error getting humidity from Nest thermostat: {e}")
            return None
    
    def get_mode(self):
        try:
            url = f"{self.base_url}/{self._get_device_path()}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            mode = data.get("traits", {}).get("sdm.devices.traits.ThermostatMode", {}).get("mode")
            # Convert Google's mode names to our standardized modes
            mode_mapping = {
                "HEAT": "heat",
                "COOL": "cool",
                "HEATCOOL": "auto",
                "OFF": "off"
            }
            return mode_mapping.get(mode, "unknown")
        except Exception as e:
            logger.error(f"Error getting mode from Nest thermostat: {e}")
            return "unknown"
    
    def set_mode(self, mode):
        try:
            # Convert our standardized modes to Google's mode names
            mode_mapping = {
                "heat": "HEAT",
                "cool": "COOL",
                "auto": "HEATCOOL",
                "off": "OFF"
            }
            google_mode = mode_mapping.get(mode.lower(), "HEAT")
            
            url = f"{self.base_url}/{self._get_device_path()}:executeCommand"
            payload = {
                "command": "sdm.devices.commands.ThermostatMode.SetMode",
                "params": {
                    "mode": google_mode
                }
            }
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error setting mode for Nest thermostat: {e}")
            return False
    
    def is_online(self):
        try:
            url = f"{self.base_url}/{self._get_device_path()}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("traits", {}).get("sdm.devices.traits.Connectivity", {}).get("status") == "ONLINE"
        except Exception as e:
            logger.error(f"Error checking online status for Nest thermostat: {e}")
            return False


class CieloThermostatAdapter(ThermostatAdapter):
    """Adapter for Cielo thermostats using IFTTT webhooks and direct API when available."""
    
    def __init__(self, device_id, api_key=None, api_token=None, ifttt_key=None):
        self.device_id = device_id
        self.api_key = api_key
        self.api_token = api_token
        self.ifttt_key = ifttt_key or settings.IFTTT_WEBHOOK_KEY
        self.ifttt_base_url = "https://maker.ifttt.com/trigger"
        self.use_direct_api = bool(api_key and api_token)
        self.direct_api_base_url = "https://api.cielowigle.com/v1"
        
    def _get_direct_api_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
    
    def _trigger_ifttt_webhook(self, event, value1=None, value2=None, value3=None):
        try:
            url = f"{self.ifttt_base_url}/{event}/with/key/{self.ifttt_key}"
            payload = {}
            if value1 is not None:
                payload["value1"] = value1
            if value2 is not None:
                payload["value2"] = value2
            if value3 is not None:
                payload["value3"] = value3
                
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error triggering IFTTT webhook: {e}")
            return False
    
    def get_temperature(self):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}"
                response = requests.get(url, headers=self._get_direct_api_headers())
                response.raise_for_status()
                data = response.json()
                return data.get("temperature")
            except Exception as e:
                logger.error(f"Error getting temperature from Cielo thermostat: {e}")
                return None
        else:
            # For IFTTT integration, we can't directly query the device
            # Return cached value from our database instead
            from thermostats.models import Thermostat
            try:
                thermostat = Thermostat.objects.get(device_id=self.device_id)
                return thermostat.current_temperature
            except Exception as e:
                logger.error(f"Error getting cached temperature for Cielo thermostat: {e}")
                return None
    
    def set_temperature(self, temperature):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}/temperature"
                payload = {"temperature": temperature}
                response = requests.post(url, headers=self._get_direct_api_headers(), json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Error setting temperature for Cielo thermostat: {e}")
                return False
        else:
            # Use IFTTT webhook to set temperature
            return self._trigger_ifttt_webhook(
                "cielo_set_temperature", 
                value1=self.device_id,
                value2=str(temperature)
            )
    
    def get_humidity(self):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}"
                response = requests.get(url, headers=self._get_direct_api_headers())
                response.raise_for_status()
                data = response.json()
                return data.get("humidity")
            except Exception as e:
                logger.error(f"Error getting humidity from Cielo thermostat: {e}")
                return None
        else:
            # For IFTTT integration, we can't directly query the device
            # Return cached value from our database instead
            from thermostats.models import Thermostat
            try:
                thermostat = Thermostat.objects.get(device_id=self.device_id)
                return thermostat.current_humidity
            except Exception as e:
                logger.error(f"Error getting cached humidity for Cielo thermostat: {e}")
                return None
    
    def get_mode(self):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}"
                response = requests.get(url, headers=self._get_direct_api_headers())
                response.raise_for_status()
                data = response.json()
                mode = data.get("mode")
                # Convert Cielo's mode names to our standardized modes
                mode_mapping = {
                    "heat": "heat",
                    "cool": "cool",
                    "auto": "auto",
                    "off": "off"
                }
                return mode_mapping.get(mode, "unknown")
            except Exception as e:
                logger.error(f"Error getting mode from Cielo thermostat: {e}")
                return "unknown"
        else:
            # For IFTTT integration, we can't directly query the device
            # Return cached value from our database instead
            from thermostats.models import Thermostat
            try:
                thermostat = Thermostat.objects.get(device_id=self.device_id)
                return thermostat.mode
            except Exception as e:
                logger.error(f"Error getting cached mode for Cielo thermostat: {e}")
                return "unknown"
    
    def set_mode(self, mode):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}/mode"
                payload = {"mode": mode}
                response = requests.post(url, headers=self._get_direct_api_headers(), json=payload)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error(f"Error setting mode for Cielo thermostat: {e}")
                return False
        else:
            # Use IFTTT webhook to set mode
            return self._trigger_ifttt_webhook(
                "cielo_set_mode", 
                value1=self.device_id,
                value2=mode
            )
    
    def is_online(self):
        if self.use_direct_api:
            try:
                url = f"{self.direct_api_base_url}/devices/{self.device_id}"
                response = requests.get(url, headers=self._get_direct_api_headers())
                response.raise_for_status()
                data = response.json()
                return data.get("online", False)
            except Exception as e:
                logger.error(f"Error checking online status for Cielo thermostat: {e}")
                return False
        else:
            # For IFTTT integration, we can't directly query the device
            # Return cached value from our database instead
            from thermostats.models import Thermostat
            try:
                thermostat = Thermostat.objects.get(device_id=self.device_id)
                return thermostat.is_online
            except Exception as e:
                logger.error(f"Error getting cached online status for Cielo thermostat: {e}")
                return False


class PioneerThermostatAdapter(ThermostatAdapter):
    """Adapter for Pioneer thermostats."""
    
    def __init__(self, device_id, api_key=None, api_token=None):
        self.device_id = device_id
        self.api_key = api_key or settings.PIONEER_API_KEY
        self.api_token = api_token or settings.PIONEER_API_TOKEN
        self.base_url = "https://api.pioneerminisplit.com/v1"
        
    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
            "X-API-Key": self.api_key
        }
    
    def get_temperature(self):
        try:
            url = f"{self.base_url}/devices/{self.device_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("current_temperature")
        except Exception as e:
            logger.error(f"Error getting temperature from Pioneer thermostat: {e}")
            return None
    
    def set_temperature(self, temperature):
        try:
            url = f"{self.base_url}/devices/{self.device_id}/temperature"
            payload = {"temperature": temperature}
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error setting temperature for Pioneer thermostat: {e}")
            return False
    
    def get_humidity(self):
        try:
            url = f"{self.base_url}/devices/{self.device_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("humidity")
        except Exception as e:
            logger.error(f"Error getting humidity from Pioneer thermostat: {e}")
            return None
    
    def get_mode(self):
        try:
            url = f"{self.base_url}/devices/{self.device_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            mode = data.get("mode")
            # Convert Pioneer's mode names to our standardized modes
            mode_mapping = {
                "heat": "heat",
                "cool": "cool",
                "auto": "auto",
                "off": "off",
                "dry": "dry",
                "fan": "fan"
            }
            return mode_mapping.get(mode, "unknown")
        except Exception as e:
            logger.error(f"Error getting mode from Pioneer thermostat: {e}")
            return "unknown"
    
    def set_mode(self, mode):
        try:
            url = f"{self.base_url}/devices/{self.device_id}/mode"
            payload = {"mode": mode}
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error setting mode for Pioneer thermostat: {e}")
            return False
    
    def is_online(self):
        try:
            url = f"{self.base_url}/devices/{self.device_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("online", True)  # Default to True if not specified
        except Exception as e:
            logger.error(f"Error checking online status for Pioneer thermostat: {e}")
            return False


class GenericThermostatAdapter(ThermostatAdapter):
    """Generic adapter for thermostats without direct API access."""
    
    def __init__(self, device_id):
        self.device_id = device_id
    
    def get_temperature(self):
        # Return cached value from our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            return thermostat.current_temperature
        except Exception as e:
            logger.error(f"Error getting cached temperature for generic thermostat: {e}")
            return None
    
    def set_temperature(self, temperature):
        # Update cached value in our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            thermostat.target_temperature = temperature
            thermostat.save(update_fields=['target_temperature'])
            return True
        except Exception as e:
            logger.error(f"Error setting temperature for generic thermostat: {e}")
            return False
    
    def get_humidity(self):
        # Return cached value from our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            return thermostat.current_humidity
        except Exception as e:
            logger.error(f"Error getting cached humidity for generic thermostat: {e}")
            return None
    
    def get_mode(self):
        # Return cached value from our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            return thermostat.mode
        except Exception as e:
            logger.error(f"Error getting cached mode for generic thermostat: {e}")
            return "unknown"
    
    def set_mode(self, mode):
        # Update cached value in our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            thermostat.mode = mode
            thermostat.save(update_fields=['mode'])
            return True
        except Exception as e:
            logger.error(f"Error setting mode for generic thermostat: {e}")
            return False
    
    def is_online(self):
        # Return cached value from our database
        from thermostats.models import Thermostat
        try:
            thermostat = Thermostat.objects.get(device_id=self.device_id)
            return thermostat.is_online
        except Exception as e:
            logger.error(f"Error getting cached online status for generic thermostat: {e}")
            return False


def get_thermostat_adapter(thermostat):
    """
    Factory function to create the appropriate thermostat adapter based on the thermostat brand.
    
    Args:
        thermostat: A Thermostat model instance
        
    Returns:
        An instance of a ThermostatAdapter subclass
    """
    if thermostat.brand == 'nest':
        return NestThermostatAdapter(
            device_id=thermostat.device_id,
            api_key=thermostat.api_key,
            api_token=thermostat.api_token
        )
    elif thermostat.brand == 'cielo':
        # Check if we have direct API credentials
        if thermostat.api_key and thermostat.api_token:
            return CieloThermostatAdapter(
                device_id=thermostat.device_id,
                api_key=thermostat.api_key,
                api_token=thermostat.api_token
            )
        else:
            # Fall back to IFTTT integration
            return CieloThermostatAdapter(
                device_id=thermostat.device_id,
                ifttt_key=thermostat.ifttt_key
            )
    elif thermostat.brand == 'pioneer':
        return PioneerThermostatAdapter(
            device_id=thermostat.device_id,
            api_key=thermostat.api_key,
            api_token=thermostat.api_token
        )
    else:
        return GenericThermostatAdapter(device_id=thermostat.device_id)
