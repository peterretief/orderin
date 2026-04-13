from django.contrib import admin
from .models import Order, OrderItem, OrderServiceAgent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'created_at')


class OrderServiceAgentInline(admin.TabularInline):
    model = OrderServiceAgent
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscriber', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subscriber__username', 'subscriber__email', 'id')
    readonly_fields = ('total_price', 'service_fee', 'total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderServiceAgentInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('total_price', 'created_at')


@admin.register(OrderServiceAgent)
class OrderServiceAgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'service_agent', 'service_type', 'price')
    list_filter = ('service_type', 'created_at')
    search_fields = ('order__id', 'service_agent__user__service_name')
    readonly_fields = ('created_at',)
