from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, ServiceAgent, MarketAgent


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser."""
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Address', {'fields': ('address', 'city', 'state', 'zip_code')}),
        ('User Type', {'fields': ('user_type', 'is_verified')}),
        ('Shop Info', {'fields': ('shop_name', 'shop_description', 'shop_logo')}),
        ('Service Info', {'fields': ('service_name', 'service_description', 'service_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')


@admin.register(ServiceAgent)
class ServiceAgentAdmin(admin.ModelAdmin):
    """Admin interface for ServiceAgent."""
    list_display = ('user', 'service_type', 'is_active', 'rating', 'total_services')
    list_filter = ('service_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__service_name')
    readonly_fields = ('created_at', 'updated_at', 'total_services')


@admin.register(MarketAgent)
class MarketAgentAdmin(admin.ModelAdmin):
    """Admin interface for MarketAgent."""
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__shop_name')
    readonly_fields = ('created_at', 'updated_at')
