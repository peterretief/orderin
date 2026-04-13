from rest_framework import serializers
from .models import CustomUser, ServiceAgent, MarketAgent


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone', 'address', 'city', 'state', 'zip_code',
            'is_verified', 'shop_name', 'service_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceAgentSerializer(serializers.ModelSerializer):
    """Serializer for ServiceAgent model."""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = ServiceAgent
        fields = [
            'id', 'user', 'service_type', 'is_active', 
            'rating', 'total_services', 'specialty', 'vehicle_type'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_services']


class MarketAgentSerializer(serializers.ModelSerializer):
    """Serializer for MarketAgent model."""
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = MarketAgent
        fields = ['id', 'user', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'phone'
        ]
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
