from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Order, OrderItem, OrderServiceAgent
from .serializers import OrderSerializer, OrderItemSerializer, CreateOrderSerializer, OrderServiceAgentSerializer
from market.models import Product
from users.models import ServiceAgent
from billing.models import UserBalance


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter orders based on user type."""
        if self.request.user.user_type == 'admin' or self.request.user.is_staff:
            return Order.objects.all()
        # Subscribers can only see their own orders
        return Order.objects.filter(subscriber=self.request.user)
    
    @action(detail=False, methods=['POST'])
    def create_order(self, request):
        """Create a new order with items and optional service agents."""
        # Only subscribers can create orders
        if request.user.user_type != 'subscriber':
            return Response(
                {'error': 'Only subscribers can create orders'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has positive balance
        try:
            balance = UserBalance.objects.get(user=request.user)
            if balance.balance <= 0:
                return Response(
                    {'error': 'Your account balance must be positive to place an order'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except UserBalance.DoesNotExist:
            return Response(
                {'error': 'Please add funds to your account first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    subscriber=request.user,
                    notes=serializer.validated_data.get('notes', '')
                )
                
                # Add items to order
                items_data = serializer.validated_data.get('items', [])
                for item_data in items_data:
                    product = get_object_or_404(Product, id=item_data['product_id'])
                    quantity = item_data['quantity']
                    
                    # Check availability
                    if product.quantity_available < quantity:
                        raise ValueError(f'{product.name} - Only {product.quantity_available} available')
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price
                    )
                
                # Add optional service agents
                services_data = serializer.validated_data.get('service_agents', [])
                for service_data in services_data:
                    service_agent = get_object_or_404(ServiceAgent, id=service_data['service_agent_id'])
                    OrderServiceAgent.objects.create(
                        order=order,
                        service_agent=service_agent,
                        service_type=service_agent.service_type,
                        price=service_data.get('price', 0),
                        notes=service_data.get('notes', '')
                    )
                
                # Calculate totals
                order.calculate_total()
                order.save()
                
                return Response(
                    OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED
                )
        
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['PUT'])
    def update_status(self, request, pk=None):
        """Update order status (admin only)."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': f'Invalid status. Must be one of: {list(dict(Order.STATUS_CHOICES).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        
        # Mark delivered when status is 'delivered'
        if new_status == 'delivered':
            from django.utils import timezone
            order.delivered_at = timezone.now()
        
        order.save()
        return Response(OrderSerializer(order).data)
    
    @action(detail=True, methods=['GET'])
    def bill_order(self, request, pk=None):
        """Bill subscriber for a delivered order."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can bill orders'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        
        if order.status != 'delivered':
            return Response(
                {'error': 'Only delivered orders can be billed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deduct from user balance in billing system
        try:
            from billing.models import UserBalance, BillingTransaction
            balance = UserBalance.objects.get(user=order.subscriber)
            balance.balance -= order.total_amount
            balance.save()
            
            # Record transaction
            BillingTransaction.objects.create(
                user=order.subscriber,
                order=order,
                amount=order.total_amount,
                type='debit',
                description=f'Billing for Order #{order.id}'
            )
            
            return Response(
                {'message': f'Order #{order.id} billed successfully',
                 'new_balance': str(balance.balance)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
