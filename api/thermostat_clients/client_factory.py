from .nest_client import NestClient
from .cielo_client import CieloClient
from .pioneer_client import PioneerClient

class ThermostatClientFactory:
    """Factory for creating thermostat API clients"""
    
    @staticmethod
    def create_client(thermostat_type, **kwargs):
        """
        Create a thermostat client based on type
        
        Args:
            thermostat_type: Type of thermostat (NEST, CIELO, PIONEER)
            **kwargs: Additional arguments for specific client
        
        Returns:
            BaseThermostatClient: An instance of the appropriate client
        """
        if thermostat_type == "NEST":
            return NestClient(
                client_id=kwargs.get("client_id"),
                client_secret=kwargs.get("client_secret"),
                redirect_uri=kwargs.get("redirect_uri"),
                project_id=kwargs.get("project_id"),
                access_token=kwargs.get("access_token"),
                refresh_token=kwargs.get("refresh_token")
            )
        elif thermostat_type == "CIELO":
            return CieloClient(
                username=kwargs.get("username"),
                password=kwargs.get("password"),
                token=kwargs.get("token")
            )
        elif thermostat_type == "PIONEER":
            return PioneerClient(
                username=kwargs.get("username"),
                password=kwargs.get("password"),
                device_key=kwargs.get("device_key")
            )
        else:
            raise ValueError(f"Unsupported thermostat type: {thermostat_type}")
