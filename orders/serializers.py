from rest_framework import serializers
from .models import Order, OrderItem, OrderServiceAgent
from market.models import Product
from users.serializers import ServiceAgentSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderServiceAgentSerializer(serializers.ModelSerializer):
    """Serializer for OrderServiceAgent model."""
    service_agent_name = serializers.CharField(source='service_agent.user.service_name', read_only=True)
    
    class Meta:
        model = OrderServiceAgent
        fields = ['id', 'order', 'service_agent', 'service_agent_name', 'service_type', 'price', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, read_only=True)
    selected_services = OrderServiceAgentSerializer(many=True, read_only=True)
    subscriber_username = serializers.CharField(source='subscriber.username', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'subscriber', 'subscriber_username', 'status', 'total_price',
            'service_fee', 'total_amount', 'notes', 'items', 'selected_services',
            'created_at', 'updated_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'total_price', 'service_fee', 'total_amount', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order with items and services."""
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            help_text='product_id and quantity'
        )
    )
    service_agents = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            help_text='service_agent_id and optional notes'
        ),
        required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, items):
        """Validate that items exist and have required fields."""
        for item in items:
            if 'product_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError('Each item must have product_id and quantity')
            if item['quantity'] <= 0:
                raise serializers.ValidationError('Quantity must be greater than 0')
        return items
    
    def create(self, validated_data):
        """Create order with items and services."""
        # This will be handled in the view
        return validated_data
