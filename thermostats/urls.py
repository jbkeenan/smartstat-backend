from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, ThermostatViewSet, CalendarEventViewSet, UsageStatisticsViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'thermostats', ThermostatViewSet, basename='thermostat')
router.register(r'calendar-events', CalendarEventViewSet, basename='calendar-event')
router.register(r'statistics', UsageStatisticsViewSet, basename='statistics')

urlpatterns = [
    path('', include(router.urls)),
]
