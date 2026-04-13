from django.contrib import admin
from .models import UserBalance, BillingTransaction, BillingPlan, AdminBilling


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BillingTransaction)
class BillingTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'balance_after', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('created_at', 'balance_after')


@admin.register(BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'amount', 'is_active')
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminBilling)
class AdminBillingAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'billing_plan', 'amount', 'status', 'billing_date', 'due_date')
    list_filter = ('status', 'billing_date', 'billing_plan')
    search_fields = ('subscriber__username', 'subscriber__email')
    readonly_fields = ('created_at', 'updated_at')
