from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from .models import CustomUser, ServiceAgent, MarketAgent
from .serializers import (
    CustomUserSerializer, ServiceAgentSerializer, 
    MarketAgentSerializer, UserRegistrationSerializer
)


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet for CustomUser model."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny()])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                CustomUserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['POST'], permission_classes=[AllowAny()])
    def login(self, request):
        """Login user."""
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response(
                CustomUserSerializer(user).data,
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user."""
        logout(request)
        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['PUT'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile."""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceAgentViewSet(viewsets.ModelViewSet):
    """ViewSet for ServiceAgent model."""
    queryset = ServiceAgent.objects.all()
    serializer_class = ServiceAgentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter service agents based on user type."""
        if self.request.user.is_staff:
            return ServiceAgent.objects.all()
        return ServiceAgent.objects.filter(is_active=True)
    
    @action(detail=False, methods=['GET'])
    def caterers(self, request):
        """Get all active caterers."""
        caterers = ServiceAgent.objects.filter(
            service_type='catering',
            is_active=True
        )
        serializer = self.get_serializer(caterers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def delivery_people(self, request):
        """Get all active delivery people."""
        delivery = ServiceAgent.objects.filter(
            service_type='delivery',
            is_active=True
        )
        serializer = self.get_serializer(delivery, many=True)
        return Response(serializer.data)


class MarketAgentViewSet(viewsets.ModelViewSet):
    """ViewSet for MarketAgent model."""
    queryset = MarketAgent.objects.all()
    serializer_class = MarketAgentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter market agents based on user type."""
        if self.request.user.is_staff:
            return MarketAgent.objects.all()
        return MarketAgent.objects.filter(is_active=True)
