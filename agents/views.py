from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ServicePrice, ServiceAvailability
from .serializers import ServicePriceSerializer, ServiceAvailabilitySerializer


class ServicePriceViewSet(viewsets.ModelViewSet):
    """ViewSet for ServicePrice model."""
    queryset = ServicePrice.objects.all()
    serializer_class = ServicePriceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def my_pricing(self, request):
        """Get pricing for current service agent."""
        if not hasattr(request.user, 'service_profile'):
            return Response(
                {'error': 'You are not a service agent'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            pricing = ServicePrice.objects.get(service_agent=request.user.service_profile)
            serializer = self.get_serializer(pricing)
            return Response(serializer.data)
        except ServicePrice.DoesNotExist:
            return Response(
                {'error': 'Pricing not set up yet'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['PUT'])
    def update_my_pricing(self, request):
        """Update pricing for current service agent."""
        if not hasattr(request.user, 'service_profile'):
            return Response(
                {'error': 'You are not a service agent'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_agent = request.user.service_profile
        pricing, created = ServicePrice.objects.get_or_create(service_agent=service_agent)
        
        serializer = self.get_serializer(pricing, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceAvailabilityViewSet(viewsets.ModelViewSet):
    """ViewSet for ServiceAvailability model."""
    queryset = ServiceAvailability.objects.all()
    serializer_class = ServiceAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter availability based on user type."""
        if hasattr(self.request.user, 'service_profile'):
            # Service agents see their own availability
            return ServiceAvailability.objects.filter(service_agent=self.request.user.service_profile)
        # Other users see all available slots
        return ServiceAvailability.objects.filter(is_available=True)
    
    @action(detail=False, methods=['GET'])
    def my_availability(self, request):
        """Get availability for current service agent."""
        if not hasattr(request.user, 'service_profile'):
            return Response(
                {'error': 'You are not a service agent'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        slots = ServiceAvailability.objects.filter(service_agent=request.user.service_profile)
        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def add_availability(self, request):
        """Add availability slot for current service agent."""
        if not hasattr(request.user, 'service_profile'):
            return Response(
                {'error': 'You are not a service agent'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        service_agent = request.user.service_profile
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(service_agent=service_agent)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['PUT'])
    def toggle_availability(self, request, pk=None):
        """Toggle availability of a slot."""
        slot = self.get_object()
        
        # Check if user is the service agent
        if not hasattr(request.user, 'service_profile') or slot.service_agent != request.user.service_profile:
            return Response(
                {'error': 'You can only update your own availability'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        slot.is_available = not slot.is_available
        slot.save()
        
        serializer = self.get_serializer(slot)
        return Response(serializer.data)
