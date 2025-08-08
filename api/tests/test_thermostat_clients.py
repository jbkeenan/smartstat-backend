import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.thermostat_clients.base_client import BaseThermostatClient
from api.thermostat_clients.nest_client import NestClient
from api.thermostat_clients.cielo_client import CieloClient
from api.thermostat_clients.pioneer_client import PioneerClient
from api.thermostat_clients.client_factory import ThermostatClientFactory

class TestThermostatClients(unittest.TestCase):
    """Test cases for thermostat client modules"""
    
    def test_client_factory(self):
        """Test that the client factory creates the correct client types"""
        # Test Nest client creation
        nest_client = ThermostatClientFactory.create_client("NEST")
        self.assertIsInstance(nest_client, NestClient)
        
        # Test Cielo client creation
        cielo_client = ThermostatClientFactory.create_client("CIELO")
        self.assertIsInstance(cielo_client, CieloClient)
        
        # Test Pioneer client creation
        pioneer_client = ThermostatClientFactory.create_client("PIONEER")
        self.assertIsInstance(pioneer_client, PioneerClient)
        
        # Test invalid type
        with self.assertRaises(ValueError):
            ThermostatClientFactory.create_client("INVALID")
    
    @patch('api.thermostat_clients.nest_client.requests.post')
    def test_nest_authentication(self, mock_post):
        """Test Nest client authentication"""
        # Mock the OAuth token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Create client and test authentication
        client = NestClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="test_redirect_uri"
        )
        
        # Test with auth code
        result = client.authenticate(auth_code="test_auth_code")
        self.assertTrue(result)
        self.assertEqual(client.access_token, "test_access_token")
        self.assertEqual(client.refresh_token, "test_refresh_token")
        
        # Test token refresh
        client.access_token = None
        result = client.authenticate()
        self.assertTrue(result)
        self.assertEqual(client.access_token, "test_access_token")
    
    @patch('api.thermostat_clients.cielo_client.requests.post')
    def test_cielo_authentication(self, mock_post):
        """Test Cielo client authentication"""
        # Mock the authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response
        
        # Create client and test authentication
        client = CieloClient(
            username="test_username",
            password="test_password"
        )
        
        result = client.authenticate()
        self.assertTrue(result)
        self.assertEqual(client.token, "test_token")
    
    @patch('api.thermostat_clients.pioneer_client.requests.post')
    def test_pioneer_authentication(self, mock_post):
        """Test Pioneer client authentication"""
        # Mock the authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "test_token",
            "expires_in": 86400
        }
        mock_post.return_value = mock_response
        
        # Create client and test authentication
        client = PioneerClient(
            username="test_username",
            password="test_password"
        )
        
        result = client.authenticate()
        self.assertTrue(result)
        self.assertEqual(client.token, "test_token")
        
        # Test with device key
        client = PioneerClient(device_key="test_device_key")
        result = client.authenticate()
        self.assertTrue(result)
        self.assertEqual(client.token, "test_device_key")
    
    @patch('api.thermostat_clients.nest_client.requests.get')
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    def test_nest_get_status(self, mock_auth, mock_get):
        """Test Nest client get_status method"""
        # Mock authentication
        mock_auth.return_value = True
        
        # Mock the status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "traits": {
                "sdm.devices.traits.Temperature": {
                    "ambientTemperatureCelsius": 22.0
                },
                "sdm.devices.traits.ThermostatMode": {
                    "mode": "HEAT"
                },
                "sdm.devices.traits.ThermostatTemperatureSetpoint": {
                    "heatCelsius": 23.0
                },
                "sdm.devices.traits.Fan": {
                    "timerMode": "OFF"
                },
                "sdm.devices.traits.Humidity": {
                    "ambientHumidityPercent": 45
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Create client and test get_status
        client = NestClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="test_redirect_uri",
            project_id="test_project_id",
            access_token="test_access_token"
        )
        
        status = client.get_status("test_device_id")
        self.assertIsNotNone(status)
        self.assertEqual(status["mode"], "heat")
        self.assertEqual(status["fan_mode"], "auto")
        self.assertTrue(status["is_online"])
        self.assertEqual(status["humidity"], 45)
        
        # Test temperature conversion (22°C should be about 71.6°F)
        self.assertAlmostEqual(status["temperature"], 71.6, delta=0.1)
    
    @patch('api.thermostat_clients.cielo_client.requests.get')
    @patch('api.thermostat_clients.cielo_client.CieloClient.authenticate')
    def test_cielo_get_status(self, mock_auth, mock_get):
        """Test Cielo client get_status method"""
        # Mock authentication
        mock_auth.return_value = True
        
        # Mock the status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_temperature": 72.0,
            "target_temperature": 74.0,
            "mode": "heat",
            "fan_mode": "auto",
            "is_online": True,
            "humidity": 40
        }
        mock_get.return_value = mock_response
        
        # Create client and test get_status
        client = CieloClient(token="test_token")
        
        status = client.get_status("test_device_id")
        self.assertIsNotNone(status)
        self.assertEqual(status["temperature"], 72.0)
        self.assertEqual(status["target_temperature"], 74.0)
        self.assertEqual(status["mode"], "heat")
        self.assertEqual(status["fan_mode"], "auto")
        self.assertTrue(status["is_online"])
        self.assertEqual(status["humidity"], 40)
    
    @patch('api.thermostat_clients.pioneer_client.requests.get')
    @patch('api.thermostat_clients.pioneer_client.PioneerClient.authenticate')
    def test_pioneer_get_status(self, mock_auth, mock_get):
        """Test Pioneer client get_status method"""
        # Mock authentication
        mock_auth.return_value = True
        
        # Mock the status response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_temperature": 70.0,
            "target_temperature": 72.0,
            "mode": "heat",
            "fan_mode": "auto",
            "is_online": True,
            "humidity": 35
        }
        mock_get.return_value = mock_response
        
        # Create client and test get_status
        client = PioneerClient(device_key="test_device_key")
        
        status = client.get_status("test_device_id")
        self.assertIsNotNone(status)
        self.assertEqual(status["temperature"], 70.0)
        self.assertEqual(status["target_temperature"], 72.0)
        self.assertEqual(status["mode"], "heat")
        self.assertEqual(status["fan_mode"], "auto")
        self.assertTrue(status["is_online"])
        self.assertEqual(status["humidity"], 35)
    
    @patch('api.thermostat_clients.nest_client.requests.post')
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    @patch('api.thermostat_clients.nest_client.NestClient.get_status')
    def test_nest_set_temperature(self, mock_get_status, mock_auth, mock_post):
        """Test Nest client set_temperature method"""
        # Mock authentication and status
        mock_auth.return_value = True
        mock_get_status.return_value = {"mode": "heat"}
        
        # Mock the set_temperature response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Create client and test set_temperature
        client = NestClient(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="test_redirect_uri",
            project_id="test_project_id",
            access_token="test_access_token"
        )
        
        result = client.set_temperature("test_device_id", 72.0)
        self.assertTrue(result)
        
        # Verify the correct command was sent
        args, kwargs = mock_post.call_args
        self.assertIn("executeCommand", args[0])
        self.assertEqual(kwargs["json"]["command"], "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat")
        
        # Test temperature conversion (72°F should be about 22.2°C)
        self.assertAlmostEqual(kwargs["json"]["params"]["heatCelsius"], 22.2, delta=0.1)

if __name__ == '__main__':
    unittest.main()
