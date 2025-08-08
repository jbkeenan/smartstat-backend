from abc import ABC, abstractmethod

class BaseThermostatClient(ABC):
    """Abstract base class for thermostat API clients"""
    
    @abstractmethod
    def authenticate(self):
        """
        Authenticate with the thermostat API
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_status(self, device_id):
        """
        Get current status of the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Status information including current temperature, target temperature,
                 mode, fan status, etc. or None if failed
        """
        pass
    
    @abstractmethod
    def set_temperature(self, device_id, temperature):
        """
        Set target temperature for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            temperature (float): Target temperature in Fahrenheit
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def set_mode(self, device_id, mode):
        """
        Set thermostat mode (heat, cool, off, etc.)
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            mode (str): Operating mode (heat, cool, auto, off)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def set_fan_mode(self, device_id, fan_mode):
        """
        Set fan mode (auto, on)
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            fan_mode (str): Fan mode (auto, on)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_schedule(self, device_id):
        """
        Get current schedule for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            
        Returns:
            dict: Schedule information or None if not supported/failed
        """
        pass
    
    @abstractmethod
    def set_schedule(self, device_id, schedule):
        """
        Set schedule for the thermostat
        
        Args:
            device_id (str): Unique identifier for the thermostat device
            schedule (dict): Schedule information in a standardized format
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
