from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin interface for site settings."""
    fields = ['currency_symbol', 'currency_name']
    
    def has_add_permission(self, request):
        """Prevent creating multiple settings objects."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting settings."""
        return False
