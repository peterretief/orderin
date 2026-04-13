from django.contrib import admin
from .models import ProductCategory, Product


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'price', 'quantity_available', 'market_agent', 'is_available')
    list_filter = ('is_available', 'category', 'market_agent', 'created_at')
    search_fields = ('name', 'sku', 'market_agent__user__shop_name')
    readonly_fields = ('created_at', 'updated_at')
