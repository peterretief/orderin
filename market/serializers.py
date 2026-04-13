from rest_framework import serializers
from .models import ProductCategory, Product, ShoppingCart, CartItem


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for ProductCategory model."""
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    shop_name = serializers.CharField(source='market_agent.user.shop_name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'market_agent', 'category', 'category_name', 'name', 
            'description', 'sku', 'price', 'quantity_available', 'unit',
            'image', 'shop_name', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'market_agent', 'shop_name', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert image field to URL."""
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation
    
    def update(self, instance, validated_data):
        """Override update to preserve image if not provided in partial update."""
        # If this is a partial update (PATCH) and image is not provided, don't change it
        if 'image' not in self.initial_data:
            validated_data.pop('image', None)
        return super().update(instance, validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    unit = serializers.CharField(source='product.unit', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image', 'unit', 'quantity', 'unit_price', 'total_price', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_product_image(self, obj):
        """Return image URL for the product."""
        if obj.product.image:
            # Return the relative URL path that will work in the browser
            return obj.product.image.url
        return None
    
    def get_unit_price(self, obj):
        return float(obj.unit_price)
    
    def get_total_price(self, obj):
        return float(obj.total_price)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for ShoppingCart model."""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ShoppingCart
        fields = ['id', 'subscriber', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'subscriber', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    
    def get_total_price(self, obj):
        return float(obj.get_total_price())
