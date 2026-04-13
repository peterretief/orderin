from django.db import models
from users.models import ServiceAgent


class ServicePrice(models.Model):
    """Pricing for different service agents."""
    
    service_agent = models.OneToOneField(ServiceAgent, on_delete=models.CASCADE, related_name='service_price')
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Base service fee')
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Additional charge per order item')
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Delivery fee per kilometer (for delivery agents)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.service_agent.user.service_name} - Pricing'


class ServiceAvailability(models.Model):
    """Availability slots for service agents."""
    
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    service_agent = models.ForeignKey(ServiceAgent, on_delete=models.CASCADE, related_name='availability_slots')
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('service_agent', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f'{self.service_agent.user.service_name} - {self.get_day_of_week_display()} {self.start_time} to {self.end_time}'
