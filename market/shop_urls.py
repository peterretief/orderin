from django.urls import path
from . import shop_views

urlpatterns = [
    path('', shop_views.shop_home, name='shop_home'),
    path('browse/', shop_views.shop_browse, name='shop_browse'),
    path('category/<int:category_id>/', shop_views.shop_category, name='shop_category'),
    path('search/', shop_views.shop_search, name='shop_search'),
    path('product/<int:product_id>/', shop_views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', shop_views.add_to_cart, name='add_to_cart'),
    path('cart/', shop_views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:product_id>/', shop_views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', shop_views.checkout, name='checkout'),
    path('delivery/<int:order_id>/', shop_views.select_delivery_method, name='select_delivery_method'),
    path('order-success/<int:order_id>/', shop_views.order_success, name='order_success'),
]
