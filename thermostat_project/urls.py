"""
URL Configuration for thermostat_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Import viewsets for compatibility routes.  These provide top‑level
# property and thermostat endpoints at `/api/properties/` and `/api/thermostats/`
# for backwards compatibility with earlier versions of the API.  They are
# registered on a separate router to avoid clashing with the names used in
# the thermostats app's router.
from thermostats.views import PropertyViewSet as CompatPropertyViewSet, ThermostatViewSet as CompatThermostatViewSet


# API root router
router = routers.DefaultRouter()

# Create a compatibility router that registers properties and thermostats at
# the root of the API.  This preserves endpoints like `/api/properties/` and
# `/api/thermostats/` which were used by earlier versions of the frontend.
compat_router = routers.DefaultRouter()
compat_router.register(r'properties', CompatPropertyViewSet, basename='compat-properties')
compat_router.register(r'thermostats', CompatThermostatViewSet, basename='compat-thermostats')

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Application APIs
    path('api/auth/', include('authentication.urls')),
    # Expose the thermostat and property APIs from the thermostats app.
    # We deliberately omit the standalone `properties` app to avoid duplicate models/endpoints.
    path('api/thermostats/', include('thermostats.urls')),

    # Include any routers that may be registered dynamically.
    path('api/', include(router.urls)),

    # Include compatibility endpoints for top‑level properties and thermostats.
    path('api/', include(compat_router.urls)),
]
