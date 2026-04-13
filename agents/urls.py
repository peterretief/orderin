from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicePriceViewSet, ServiceAvailabilityViewSet

router = DefaultRouter()
router.register(r'pricing', ServicePriceViewSet, basename='service-price')
router.register(r'availability', ServiceAvailabilityViewSet, basename='service-availability')

urlpatterns = [
    path('', include(router.urls)),
]
