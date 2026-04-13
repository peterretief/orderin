from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with different user types."""
    
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('subscriber', 'Subscriber'),
        ('market_agent', 'Market Agent'),
        ('caterer', 'Caterer'),
        ('delivery_person', 'Delivery Person'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='subscriber')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For market agents
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    shop_description = models.TextField(blank=True, null=True)
    shop_logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    
    # For service agents (caterers, delivery)
    service_name = models.CharField(max_length=255, blank=True, null=True)
    service_description = models.TextField(blank=True, null=True)
    service_image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    
    # User preferences
    currency_symbol = models.CharField(max_length=10, default='R', help_text='Preferred currency symbol (e.g., $, €, R)')
    
    # Banking information
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_holder_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_branch_code = models.CharField(max_length=20, blank=True, null=True)
    bank_account_type = models.CharField(
        max_length=20,
        choices=[
            ('savings', 'Savings Account'),
            ('checking', 'Cheque Account'),
            ('business', 'Business Account'),
            ('other', 'Other'),
        ],
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class ServiceAgent(models.Model):
    """Service agents (Caterers and Delivery People) available services."""
    
    SERVICE_TYPE_CHOICES = (
        ('catering', 'Catering'),
        ('delivery', 'Delivery'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='service_profile')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_services = models.IntegerField(default=0)
    
    # For delivery people
    vehicle_type = models.CharField(max_length=100, blank=True, null=True)
    max_weight_capacity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # For caterers
    specialty = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.service_name} - {self.get_service_type_display()}'


class MarketAgent(models.Model):
    """Market agents who manage produce/ingredients inventory."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='market_profile')
    is_active = models.BooleanField(default=True)
    
    # Certifications and farm information
    is_organic = models.BooleanField(default=False, help_text='Is this farm certified organic?')
    is_gmo_free = models.BooleanField(default=False, help_text='Are products GMO-free?')
    certifications = models.TextField(
        blank=True, 
        null=True,
        help_text='e.g., SAPO Organic, Fair Trade, Rainforest Alliance, etc.'
    )
    farm_description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of farm practices, what you grow, etc.'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.shop_name} Market Agent'
