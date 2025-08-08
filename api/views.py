from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Property, Thermostat, Calendar, Schedule, TemperatureLog, UserProfile
from .serializers import (
    UserSerializer, PropertySerializer, ThermostatSerializer, 
    CalendarSerializer, ScheduleSerializer, TemperatureLogSerializer,
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows properties to be viewed or edited.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter properties to return only those belonging to the current user"""
        return Property.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user field to the current user when creating a property"""
        serializer.save(user=self.request.user)


class ThermostatViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows thermostats to be viewed or edited.
    """
    queryset = Thermostat.objects.all()
    serializer_class = ThermostatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter thermostats to return only those belonging to the current user's properties"""
        user_properties = Property.objects.filter(user=self.request.user)
        return Thermostat.objects.filter(property__in=user_properties)


class CalendarViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows calendars to be viewed or edited.
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter calendars to return only those belonging to the current user's properties"""
        user_properties = Property.objects.filter(user=self.request.user)
        return Calendar.objects.filter(property__in=user_properties)


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows schedules to be viewed or edited.
    """
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter schedules to return only those belonging to the current user's thermostats"""
        user_properties = Property.objects.filter(user=self.request.user)
        user_thermostats = Thermostat.objects.filter(property__in=user_properties)
        return Schedule.objects.filter(thermostat__in=user_thermostats)


class TemperatureLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows temperature logs to be viewed.
    """
    queryset = TemperatureLog.objects.all()
    serializer_class = TemperatureLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter temperature logs to return only those belonging to the current user's thermostats"""
        user_properties = Property.objects.filter(user=self.request.user)
        user_thermostats = Thermostat.objects.filter(property__in=user_properties)
        return TemperatureLog.objects.filter(thermostat__in=user_thermostats)


class UserRegistrationView(APIView):
    """
    API endpoint for user registration.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API endpoint for retrieving and updating user profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
