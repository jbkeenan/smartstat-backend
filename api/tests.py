from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Property, Thermostat, Calendar, Schedule, UserProfile

class AuthenticationTests(TestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        
    def test_user_login(self):
        """Test user login endpoint"""
        # Create a user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        UserProfile.objects.create(user=user)
        
        # Login
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('user' in response.data)
        
    def test_user_profile(self):
        """Test user profile endpoint"""
        # Create a user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        UserProfile.objects.create(user=user, phone='1234567890', company='Test Company')
        
        # Login
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']
        
        # Get profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '1234567890')
        self.assertEqual(response.data['company'], 'Test Company')


class PropertyTests(TestCase):
    """Test property endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        UserProfile.objects.create(user=self.user)
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_url = reverse('login')
        login_response = self.client.post(login_url, login_data, format='json')
        self.token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # URLs
        self.properties_url = reverse('property-list')
        
        # Test data
        self.property_data = {
            'name': 'Test Property',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'country': 'Test Country'
        }
        
    def test_create_property(self):
        """Test creating a property"""
        response = self.client.post(self.properties_url, self.property_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(Property.objects.get().name, 'Test Property')
        self.assertEqual(Property.objects.get().user, self.user)
        
    def test_list_properties(self):
        """Test listing properties"""
        # Create a property
        Property.objects.create(
            name=self.property_data['name'],
            address=self.property_data['address'],
            city=self.property_data['city'],
            state=self.property_data['state'],
            zip_code=self.property_data['zip_code'],
            country=self.property_data['country'],
            user=self.user
        )
        
        # Create another property for a different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        Property.objects.create(
            name='Other Property',
            address='456 Other St',
            city='Other City',
            state='OS',
            zip_code='67890',
            country='Other Country',
            user=other_user
        )
        
        # List properties
        response = self.client.get(self.properties_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Should only see own properties
        self.assertEqual(response.data['results'][0]['name'], 'Test Property')


class ThermostatTests(TestCase):
    """Test thermostat endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        UserProfile.objects.create(user=self.user)
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_url = reverse('login')
        login_response = self.client.post(login_url, login_data, format='json')
        self.token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create a property
        self.property = Property.objects.create(
            name='Test Property',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            country='Test Country',
            user=self.user
        )
        
        # URLs
        self.thermostats_url = reverse('thermostat-list')
        
        # Test data
        self.thermostat_data = {
            'name': 'Test Thermostat',
            'device_id': 'test123',
            'type': 'NEST',
            'property': self.property.id
        }
        
    def test_create_thermostat(self):
        """Test creating a thermostat"""
        response = self.client.post(self.thermostats_url, self.thermostat_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Thermostat.objects.count(), 1)
        self.assertEqual(Thermostat.objects.get().name, 'Test Thermostat')
        self.assertEqual(Thermostat.objects.get().property, self.property)
