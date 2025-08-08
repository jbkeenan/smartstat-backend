#!/usr/bin/env python
import unittest
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_thermostat_clients import TestThermostatClients
from tests.test_thermostat_api_extension import TestThermostatAPIExtension

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestThermostatClients))
    test_suite.addTest(unittest.makeSuite(TestThermostatAPIExtension))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate status code
    sys.exit(not result.wasSuccessful())
