from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import ProductCategory, Product, ShoppingCart, CartItem
from .serializers import ProductCategorySerializer, ProductSerializer, ShoppingCartSerializer, CartItemSerializer


class IsMarketAgent(permissions.BasePermission):
    """Permission for market agents."""
    def has_permission(self, request, view):
        return request.user.user_type == 'market_agent'


class IsSubscriber(permissions.BasePermission):
    """Permission for subscribers."""
    def has_permission(self, request, view):
        return request.user.user_type == 'subscriber'


class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ProductCategory model."""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # Disable pagination for categories


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model with agent upload support."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = None  # Disable pagination to return all products
    
    def get_permissions(self):
        """Allow anonymous read access, but require authentication for write operations."""
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'my_products'):
            return [IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Filter products based on user type."""
        if self.request.user.is_authenticated and self.request.user.user_type == 'market_agent':
            # Market agents see their own products and can also browse others
            return Product.objects.all()
        # All users (including anonymous) can see available products
        return Product.objects.filter(is_available=True)
    
    def perform_create(self, serializer):
        """Override create to set market_agent from request user."""
        if self.request.user.user_type != 'market_agent':
            raise PermissionDenied('Only market agents can upload products')
        
        from users.models import MarketAgent
        market_agent = MarketAgent.objects.filter(user=self.request.user).first()
        
        if not market_agent:
            raise PermissionDenied('User does not have a market agent profile')
        
        serializer.save(market_agent=market_agent)
    
    def perform_update(self, serializer):
        """Ensure agents can only update their own products."""
        product = self.get_object()
        if self.request.user.user_type == 'market_agent':
            if product.market_agent.user != self.request.user:
                raise PermissionDenied('You can only update your own products')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure agents can only delete their own products."""
        if self.request.user.is_authenticated and self.request.user.user_type == 'market_agent':
            if instance.market_agent.user != self.request.user:
                raise PermissionDenied('You can only delete your own products')
        instance.delete()
    
    @action(detail=False, methods=['GET'])
    def my_products(self, request):
        """Get products uploaded by the current market agent."""
        if request.user.user_type != 'market_agent':
            return Response(
                {'error': 'Only market agents can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from users.models import MarketAgent
        market_agent = MarketAgent.objects.filter(user=request.user).first()
        products = Product.objects.filter(market_agent=market_agent)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_category(self, request):
        """Get products filtered by category."""
        category_id = request.query_params.get('category_id')
        if category_id:
            products = self.get_queryset().filter(category_id=category_id)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'category_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['GET'])
    def by_shop(self, request):
        """Get products from a specific shop."""
        market_agent_id = request.query_params.get('market_agent_id')
        if market_agent_id:
            products = self.get_queryset().filter(market_agent_id=market_agent_id)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'error': 'market_agent_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['PUT'])
    def update_availability(self, request, pk=None):
        """Update product availability and quantity."""
        product = self.get_object()
        
        # Check if user is the market agent
        if request.user.user_type == 'market_agent':
            if product.market_agent.user != request.user:
                return Response(
                    {'error': 'You can only update your own products'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        quantity = request.data.get('quantity_available')
        is_available = request.data.get('is_available')
        
        if quantity is not None:
            product.quantity_available = quantity
        if is_available is not None:
            product.is_available = is_available
        
        product.save()
        return Response(self.get_serializer(product).data)


class ShoppingCartViewSet(viewsets.ViewSet):
    """ViewSet for Shopping Cart operations."""
    permission_classes = [IsAuthenticated, IsSubscriber]
    
    @action(detail=False, methods=['GET'])
    def view_cart(self, request):
        """View the current shopping cart."""
        cart, created = ShoppingCart.objects.get_or_create(subscriber=request.user)
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def add_item(self, request):
        """Add an item to the shopping cart."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                return Response(
                    {'error': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        if product.quantity_available < quantity:
            return Response(
                {'error': f'Not enough stock. Available: {product.quantity_available}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
        
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                # Update quantity if item already exists
                cart_item.quantity += quantity
                cart_item.save()
            
            cart.save()
        
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['POST'])
    def remove_item(self, request):
        """Remove an item from the shopping cart."""
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(ShoppingCart, subscriber=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        cart_item.delete()
        
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def update_item_quantity(self, request):
        """Update quantity of an item in the cart."""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        
        if not product_id or quantity is None:
            return Response(
                {'error': 'product_id and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                return Response(
                    {'error': 'Quantity must be at least 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = get_object_or_404(ShoppingCart, subscriber=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        product = cart_item.product
        
        if product.quantity_available < quantity:
            return Response(
                {'error': f'Not enough stock. Available: {product.quantity_available}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def clear_cart(self, request):
        """Clear all items from the shopping cart."""
        cart = get_object_or_404(ShoppingCart, subscriber=request.user)
        cart.items.all().delete()
        
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)
