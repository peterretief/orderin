from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet, ShoppingCartViewSet

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', ShoppingCartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
