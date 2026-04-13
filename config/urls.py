"""
URL configuration for Order In.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.auth_views import login_view, logout_view, home_view, edit_profile

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', edit_profile, name='edit_profile'),
    path('admin/', admin.site.urls),
    path('dashboards/', include('dashboards.urls')),
    path('shop/', include('market.shop_urls')),
    path('agent/', include('users.agent_urls')),
    path('api/users/', include('users.urls')),
    path('api/market/', include('market.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/agents/', include('agents.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/delivery/', include('delivery.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
