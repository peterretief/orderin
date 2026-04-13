from rest_framework import serializers
from .models import UserBalance, BillingTransaction, BillingPlan, AdminBilling, BusinessAccount, BusinessTransaction, PayoutRequest, AdminFeeConfig


class UserBalanceSerializer(serializers.ModelSerializer):
    """Serializer for UserBalance model."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserBalance
        fields = ['id', 'user', 'username', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BillingTransactionSerializer(serializers.ModelSerializer):
    """Serializer for BillingTransaction model."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BillingTransaction
        fields = [
            'id', 'user', 'username', 'order', 'amount', 'type', 
            'description', 'balance_after', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'balance_after']


class BillingPlanSerializer(serializers.ModelSerializer):
    """Serializer for BillingPlan model."""
    
    class Meta:
        model = BillingPlan
        fields = [
            'id', 'name', 'description', 'plan_type', 'amount', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminBillingSerializer(serializers.ModelSerializer):
    """Serializer for AdminBilling model."""
    username = serializers.CharField(source='subscriber.username', read_only=True)
    plan_name = serializers.CharField(source='billing_plan.name', read_only=True)
    
    class Meta:
        model = AdminBilling
        fields = [
            'id', 'subscriber', 'username', 'billing_plan', 'plan_name',
            'amount', 'status', 'billing_date', 'due_date', 'paid_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BusinessAccountSerializer(serializers.ModelSerializer):
    """Serializer for BusinessAccount model."""
    
    class Meta:
        model = BusinessAccount
        fields = [
            'id', 'name', 'status', 'description', 'total_balance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_balance']


class BusinessTransactionSerializer(serializers.ModelSerializer):
    """Serializer for BusinessTransaction model."""
    subscriber_username = serializers.CharField(source='subscriber.username', read_only=True)
    market_agent_user = serializers.CharField(source='market_agent.user.username', read_only=True)
    service_agent_user = serializers.CharField(source='service_agent.user.username', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    
    class Meta:
        model = BusinessTransaction
        fields = [
            'id', 'business_account', 'subscriber', 'subscriber_username',
            'market_agent', 'market_agent_user', 'service_agent', 'service_agent_user',
            'order', 'order_id', 'type', 'amount', 'description',
            'balance_before', 'balance_after', 'reference_id', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'balance_before', 'balance_after',
            'subscriber_username', 'market_agent_user', 'service_agent_user', 'order_id'
        ]


class PayoutRequestSerializer(serializers.ModelSerializer):
    """Serializer for PayoutRequest model."""
    agent_username = serializers.SerializerMethodField()
    
    class Meta:
        model = PayoutRequest
        fields = [
            'id', 'agent', 'service_agent', 'agent_type', 'agent_username',
            'amount_requested', 'amount_approved', 'status',
            'requested_at', 'approved_at', 'paid_at',
            'admin_notes', 'business_transaction'
        ]
        read_only_fields = [
            'id', 'requested_at', 'approved_at', 'paid_at',
            'business_transaction'
        ]
    
    def get_agent_username(self, obj):
        if obj.agent:
            return obj.agent.user.username
        elif obj.service_agent:
            return obj.service_agent.user.username
        return None


class AdminFeeConfigSerializer(serializers.ModelSerializer):
    """Serializer for AdminFeeConfig model."""
    
    class Meta:
        model = AdminFeeConfig
        fields = [
            'id', 'fee_type', 'fixed_amount', 'percentage', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
