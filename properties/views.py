from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Property, PropertySettings
from .serializers import PropertySerializer, PropertySettingsSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing properties.
    """
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        This view returns a list of all properties
        for the currently authenticated user.
        """
        user = self.request.user
        return Property.objects.filter(owner=user)
    
    @action(detail=True, methods=['get', 'put', 'patch'])
    def settings(self, request, pk=None):
        """
        Retrieve or update property settings.
        """
        property_instance = get_object_or_404(Property, pk=pk, owner=request.user)
        settings_instance = get_object_or_404(PropertySettings, property=property_instance)
        
        if request.method == 'GET':
            serializer = PropertySettingsSerializer(settings_instance)
            return Response(serializer.data)
        
        # Update settings
        serializer = PropertySettingsSerializer(settings_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
