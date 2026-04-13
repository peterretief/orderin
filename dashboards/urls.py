from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.admin_users_management, name='admin_users'),
    path('admin/products/', admin_views.admin_products_management, name='admin_products'),
    path('admin/orders/', admin_views.admin_orders_management, name='admin_orders'),
    path('admin/analytics/', admin_views.admin_analytics, name='admin_analytics'),
    path('subscriber/', views.subscriber_dashboard, name='subscriber_dashboard'),
    path('market-agent/', views.market_agent_dashboard, name='market_agent_dashboard'),
    path('service-agent/', views.service_agent_dashboard, name='service_agent_dashboard'),
    path('delivery-agent/', views.delivery_agent_dashboard, name='delivery_agent_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
]
