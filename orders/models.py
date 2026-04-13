from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser, ServiceAgent
from market.models import Product


class Order(models.Model):
    """Orders placed by subscribers."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('confirmed', 'Confirmed'),
        ('being_prepared', 'Being Prepared'),
        ('ready_for_delivery', 'Ready for Delivery'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment tracking
    is_paid = models.BooleanField(default=False)
    payment_verified = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order #{self.id} - {self.subscriber.username} ({self.status})'
    
    def calculate_total(self):
        """Calculate total amount including services."""
        items_total = sum(item.total_price for item in self.items.all())
        service_fee = sum(service.price for service in self.selected_services.all())
        self.total_price = items_total
        self.service_fee = service_fee
        self.total_amount = items_total + service_fee
        return self.total_amount


class OrderItem(models.Model):
    """Individual items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Calculate total price when saving."""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.product.name} x{self.quantity}'


class OrderServiceAgent(models.Model):
    """Link between orders and selected service agents."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='selected_services')
    service_agent = models.ForeignKey(ServiceAgent, on_delete=models.PROTECT, related_name='orders')
    
    service_type = models.CharField(max_length=20)  # catering or delivery
    price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('order', 'service_agent')
    
    def __str__(self):
        return f'{self.service_agent.user.service_name} for Order #{self.order.id}'
