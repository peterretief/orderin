from django.db import models
from django.core.validators import MinValueValidator
from users.models import MarketAgent, CustomUser


class ProductCategory(models.Model):
    """Categories for produce/ingredients."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Products offered by market agents."""
    market_agent = models.ForeignKey(MarketAgent, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.IntegerField(default=0)
    unit = models.CharField(max_length=50)  # kg, piece, liter, etc
    
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Certifications and sourcing info
    is_organic = models.BooleanField(default=False, help_text='Is this product certified organic?')
    is_gmo_free = models.BooleanField(default=False, help_text='Is this product GMO-free?')
    certifications = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='e.g., SAPO Organic, Fair Trade, etc.'
    )
    
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('market_agent', 'sku')
    
    def __str__(self):
        return f'{self.name} - {self.market_agent.user.shop_name}'


class ShoppingCart(models.Model):
    """Shopping cart for subscribers."""
    subscriber = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='shopping_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'Cart for {self.subscriber.username}'
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_total_price(self):
        """Get total price of all items."""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a shopping cart."""
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.product.name} x{self.quantity} in {self.cart.subscriber.username}\'s cart'
    
    @property
    def unit_price(self):
        """Get the product price at time of addition."""
        return self.product.price
    
    @property
    def total_price(self):
        """Calculate total price for this item."""
        return self.quantity * self.unit_price
