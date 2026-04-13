from django.urls import path
from . import agent_views

urlpatterns = [
    path('upload-products/', agent_views.upload_products, name='upload_products'),
    path('my-products/', agent_views.my_products, name='my_products'),
    path('dashboard/', agent_views.agent_dashboard, name='agent_dashboard'),
    path('edit-address/', agent_views.edit_agent_address, name='edit_agent_address'),
]
