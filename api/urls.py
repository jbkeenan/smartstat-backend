from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, PropertyViewSet, ThermostatViewSet, 
    CalendarViewSet, ScheduleViewSet, TemperatureLogViewSet,
    UserRegistrationView, UserLoginView, UserProfileView
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'properties', PropertyViewSet)
router.register(r'thermostats', ThermostatViewSet)
router.register(r'calendars', CalendarViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'temperature-logs', TemperatureLogViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include the router URLs
    path('', include(router.urls)),
]
