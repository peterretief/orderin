from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cold-chain-requirements', views.ColdChainRequirementViewSet, basename='cold-chain-requirement')
router.register(r'vehicles', views.DeliveryVehicleViewSet, basename='vehicle')
router.register(r'methods', views.DeliveryMethodViewSet, basename='method')
router.register(r'collection-points', views.CollectionPointViewSet, basename='collection-point')
router.register(r'order-deliveries', views.OrderDeliveryViewSet, basename='order-delivery')
router.register(r'tracking', views.DeliveryTrackingViewSet, basename='tracking')
router.register(r'tracking-events', views.DeliveryTrackingEventViewSet, basename='tracking-event')
router.register(r'assignments', views.DeliveryAssignmentViewSet, basename='assignment')
router.register(r'compliance-reports', views.DeliveryComplianceReportViewSet, basename='compliance-report')
router.register(r'location-history', views.DeliveryLocationHistoryViewSet, basename='location-history')
router.register(r'routes', views.DeliveryRouteViewSet, basename='route')
router.register(r'route-stops', views.RouteStopViewSet, basename='route-stop')
router.register(r'planning-settings', views.RoutePlanningSettingViewSet, basename='planning-setting')

urlpatterns = [
    path('', include(router.urls)),
    path('calculate-cost/', views.calculate_delivery_cost, name='calculate-delivery-cost'),
    path('validate-address/', views.validate_address, name='validate-address'),
]
