from rest_framework import serializers
from .models import ServicePrice, ServiceAvailability


class ServicePriceSerializer(serializers.ModelSerializer):
    """Serializer for ServicePrice model."""
    service_agent_name = serializers.CharField(source='service_agent.user.service_name', read_only=True)
    
    class Meta:
        model = ServicePrice
        fields = [
            'id', 'service_agent', 'service_agent_name', 'base_price', 
            'price_per_item', 'price_per_km', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for ServiceAvailability model."""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    service_agent_name = serializers.CharField(source='service_agent.user.service_name', read_only=True)
    
    class Meta:
        model = ServiceAvailability
        fields = [
            'id', 'service_agent', 'service_agent_name', 'day_of_week', 
            'day_name', 'start_time', 'end_time', 'is_available', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
