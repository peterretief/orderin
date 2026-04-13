from django.contrib import admin
from .models import ServicePrice, ServiceAvailability


@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ('service_agent', 'base_price', 'price_per_item', 'price_per_km')
    search_fields = ('service_agent__user__service_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('service_agent', 'get_day_name', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'service_agent')
    search_fields = ('service_agent__user__service_name',)
    
    def get_day_name(self, obj):
        return obj.get_day_of_week_display()
    get_day_name.short_description = 'Day'
