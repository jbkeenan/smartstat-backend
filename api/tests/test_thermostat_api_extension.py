import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add the parent directory to sys.path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.thermostat_api_extension import extend_thermostat_viewset

class TestThermostatAPIExtension(unittest.TestCase):
    """Test cases for thermostat API extension"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock ThermostatViewSet class
        class MockThermostatViewSet:
            def get_object(self):
                thermostat = MagicMock()
                thermostat.type = "NEST"
                thermostat.device_id = "test_device_id"
                thermostat.api_key = json.dumps({
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                    "access_token": "test_access_token"
                })
                return thermostat
        
        # Extend the mock class with our API extension
        self.ViewSetClass = extend_thermostat_viewset(MockThermostatViewSet)
        self.viewset = self.ViewSetClass()
    
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    @patch('api.thermostat_clients.nest_client.NestClient.get_status')
    def test_status_endpoint(self, mock_get_status, mock_authenticate):
        """Test the status endpoint"""
        # Mock authentication and status
        mock_authenticate.return_value = True
        mock_get_status.return_value = {
            "temperature": 72.0,
            "target_temperature": 74.0,
            "mode": "heat",
            "fan_mode": "auto",
            "is_online": True,
            "humidity": 40
        }
        
        # Create a mock request
        request = MagicMock()
        
        # Call the status endpoint
        response = self.viewset.status(request, pk=1)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["temperature"], 72.0)
        self.assertEqual(response.data["mode"], "heat")
    
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    @patch('api.thermostat_clients.nest_client.NestClient.set_temperature')
    def test_set_temperature_endpoint(self, mock_set_temperature, mock_authenticate):
        """Test the set_temperature endpoint"""
        # Mock authentication and set_temperature
        mock_authenticate.return_value = True
        mock_set_temperature.return_value = True
        
        # Create a mock request
        request = MagicMock()
        request.data = {"temperature": 72.0}
        
        # Call the set_temperature endpoint
        response = self.viewset.set_temperature(request, pk=1)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
    
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    @patch('api.thermostat_clients.nest_client.NestClient.set_mode')
    def test_set_mode_endpoint(self, mock_set_mode, mock_authenticate):
        """Test the set_mode endpoint"""
        # Mock authentication and set_mode
        mock_authenticate.return_value = True
        mock_set_mode.return_value = True
        
        # Create a mock request
        request = MagicMock()
        request.data = {"mode": "heat"}
        
        # Call the set_mode endpoint
        response = self.viewset.set_mode(request, pk=1)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
    
    @patch('api.thermostat_clients.nest_client.NestClient.authenticate')
    @patch('api.thermostat_clients.nest_client.NestClient.set_fan_mode')
    def test_set_fan_mode_endpoint(self, mock_set_fan_mode, mock_authenticate):
        """Test the set_fan_mode endpoint"""
        # Mock authentication and set_fan_mode
        mock_authenticate.return_value = True
        mock_set_fan_mode.return_value = True
        
        # Create a mock request
        request = MagicMock()
        request.data = {"fan_mode": "auto"}
        
        # Call the set_fan_mode endpoint
        response = self.viewset.set_fan_mode(request, pk=1)
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
    
    def test_get_client_kwargs(self):
        """Test the _get_client_kwargs method"""
        # Get client kwargs for NEST
        thermostat = MagicMock()
        thermostat.type = "NEST"
        thermostat.api_key = json.dumps({
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "access_token": "test_access_token"
        })
        
        kwargs = self.viewset._get_client_kwargs(thermostat)
        
        # Verify the kwargs
        self.assertEqual(kwargs["client_id"], "test_client_id")
        self.assertEqual(kwargs["client_secret"], "test_client_secret")
        self.assertEqual(kwargs["access_token"], "test_access_token")
        
        # Test with different thermostat type
        thermostat.type = "CIELO"
        thermostat.api_key = json.dumps({
            "username": "test_username",
            "password": "test_password"
        })
        
        kwargs = self.viewset._get_client_kwargs(thermostat)
        
        # Verify the kwargs
        self.assertEqual(kwargs["username"], "test_username")
        self.assertEqual(kwargs["password"], "test_password")

if __name__ == '__main__':
    unittest.main()
