from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserBalanceViewSet, BillingTransactionViewSet,
    BillingPlanViewSet, AdminBillingViewSet, BusinessAccountViewSet, BusinessTransactionViewSet,
    PayoutRequestViewSet
)
from .receipt_views import transaction_history, generate_receipt, order_receipt
from .admin_views import business_account_dashboard, transaction_detail, transactions_by_type, bank_statement
from .agent_views import market_agent_statement, service_agent_statement

router = DefaultRouter()
router.register(r'balance', UserBalanceViewSet, basename='user-balance')
router.register(r'transactions', BillingTransactionViewSet, basename='billing-transaction')
router.register(r'plans', BillingPlanViewSet, basename='billing-plan')
router.register(r'admin-billing', AdminBillingViewSet, basename='admin-billing')
router.register(r'business-account', BusinessAccountViewSet, basename='business-account')
router.register(r'business-transactions', BusinessTransactionViewSet, basename='business-transaction')
router.register(r'payout-requests', PayoutRequestViewSet, basename='payout-request')

urlpatterns = [
    path('', include(router.urls)),
    path('history/', transaction_history, name='transaction_history'),
    path('receipt/<int:transaction_id>/', generate_receipt, name='transaction_receipt'),
    path('order-receipt/<int:order_id>/', order_receipt, name='order_receipt'),
    # Business Account Dashboard
    path('dashboard/business-account/', business_account_dashboard, name='business_account_dashboard'),
    path('dashboard/transaction/<int:transaction_id>/', transaction_detail, name='transaction_detail'),
    path('dashboard/transactions/<str:transaction_type>/', transactions_by_type, name='transactions_by_type'),
    path('dashboard/bank-statement/', bank_statement, name='bank_statement'),
    # Agent Statements
    path('dashboard/market-agent-statement/', market_agent_statement, name='market_agent_statement'),
    path('dashboard/service-agent-statement/', service_agent_statement, name='service_agent_statement'),
]
