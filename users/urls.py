from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, ServiceAgentViewSet, MarketAgentViewSet

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='user')
router.register(r'service-agents', ServiceAgentViewSet, basename='service-agent')
router.register(r'market-agents', MarketAgentViewSet, basename='market-agent')

urlpatterns = [
    path('', include(router.urls)),
]
