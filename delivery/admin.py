from django.contrib import admin
from .models import (
    ColdChainRequirement,
    DeliveryVehicle,
    DeliveryMethod,
    CollectionPoint,
    OrderDelivery,
    DeliveryTracking,
    DeliveryTrackingEvent,
    DeliveryAssignment,
    DeliveryComplianceReport,
    DeliveryLocationHistory,
    DeliveryRoute,
    RouteStop,
    RoutePlanningSetting,
    DeliveryPricingTier,
    WeightBasedPricing,
    TempControlPricing,
    DeliveryCost,
)


@admin.register(ColdChainRequirement)
class ColdChainRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage_type', 'min_temperature', 'max_temperature', 'product')
    list_filter = ('storage_type', 'created_at')
    search_fields = ('name', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryVehicle)
class DeliveryVehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'vehicle_type', 'service_agent', 'is_active')
    list_filter = ('vehicle_type', 'is_active', 'has_temperature_control')
    search_fields = ('registration_number', 'vehicle_make_model', 'service_agent__user__service_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'method_type', 'is_active')
    list_filter = ('method_type', 'is_active')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CollectionPoint)
class CollectionPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'location_type', 'is_active', 'current_orders_count')
    list_filter = ('location_type', 'is_active', 'city')
    search_fields = ('name', 'address', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrderDelivery)
class OrderDeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_method', 'delivery_status', 'cold_chain_compliance')
    list_filter = ('delivery_status', 'cold_chain_compliance', 'created_at')
    search_fields = ('order__id', 'delivery_address', 'collection_point__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('delivery_assignment', 'vehicle_temperature_status', 'current_temperature', 'tracked_at')
    list_filter = ('vehicle_temperature_status', 'tracked_at')
    search_fields = ('delivery_assignment__delivery_agent__user__service_name',)
    readonly_fields = ('tracked_at', 'created_at', 'updated_at')


@admin.register(DeliveryTrackingEvent)
class DeliveryTrackingEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_severity', 'requires_action', 'created_at')
    list_filter = ('event_type', 'event_severity', 'requires_action', 'created_at')
    search_fields = ('event_description', 'delivery_tracking__delivery_assignment__delivery_agent__user__service_name')
    readonly_fields = ('created_at',)


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery_agent', 'assignment_status', 'delivery_fee', 'assigned_at')
    list_filter = ('assignment_status', 'cold_chain_monitoring_enabled', 'assigned_at')
    search_fields = ('delivery_agent__user__service_name', 'order_delivery__order__id')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at')


@admin.register(DeliveryComplianceReport)
class DeliveryComplianceReportAdmin(admin.ModelAdmin):
    list_display = ('delivery_assignment', 'compliance_status', 'critical_events_count', 'generated_at')
    list_filter = ('compliance_status', 'generated_at')
    search_fields = ('delivery_assignment__delivery_agent__user__service_name',)
    readonly_fields = ('generated_at',)


@admin.register(DeliveryLocationHistory)
class DeliveryLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('delivery_assignment', 'latitude', 'longitude', 'speed', 'recorded_at')
    list_filter = ('recorded_at', 'speed')
    search_fields = ('delivery_assignment__delivery_agent__user__service_name', 'location_address')
    readonly_fields = ('recorded_at',)


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(admin.ModelAdmin):
    list_display = ('delivery_agent', 'route_date', 'status', 'total_deliveries', 'completed_deliveries')
    list_filter = ('status', 'route_date')
    search_fields = ('delivery_agent__user__service_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    list_display = ('delivery_route', 'sequence', 'destination_name', 'status', 'estimated_arrival_time')
    list_filter = ('status', 'delivery_route__route_date')
    search_fields = ('destination_address', 'destination_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RoutePlanningSetting)
class RoutePlanningSettingAdmin(admin.ModelAdmin):
    list_display = ('service_agent', 'optimization_algorithm', 'max_deliveries_per_day')
    list_filter = ('optimization_algorithm',)
    search_fields = ('service_agent__user__service_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryPricingTier)
class DeliveryPricingTierAdmin(admin.ModelAdmin):
    list_display = ('delivery_method', 'min_distance', 'max_distance', 'base_price', 'is_active')
    list_filter = ('delivery_method', 'is_active', 'distance_unit')
    search_fields = ('delivery_method__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WeightBasedPricing)
class WeightBasedPricingAdmin(admin.ModelAdmin):
    list_display = ('min_weight_kg', 'max_weight_kg', 'surcharge_percentage', 'surcharge_fixed', 'is_active')
    list_filter = ('is_active', 'applies_to_all_methods')
    search_fields = ('notes',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('delivery_methods',)


@admin.register(TempControlPricing)
class TempControlPricingAdmin(admin.ModelAdmin):
    list_display = ('storage_type', 'surcharge_percentage', 'surcharge_fixed', 'requires_vehicle_capability', 'is_active')
    list_filter = ('storage_type', 'is_active', 'requires_vehicle_capability')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryCost)
class DeliveryCostAdmin(admin.ModelAdmin):
    list_display = ('order_delivery', 'base_price', 'total_cost', 'calculated_at')
    list_filter = ('calculated_at', 'currency')
    search_fields = ('order_delivery__order__id',)
    readonly_fields = ('calculated_at', 'updated_at', 'subtotal', 'total_cost', 'tax_amount')
    
    fieldsets = (
        ('Order Delivery', {
            'fields': ('order_delivery',)
        }),
        ('Cost Components', {
            'fields': ('base_price', 'distance_km', 'distance_charge', 'actual_weight_kg', 'weight_surcharge')
        }),
        ('Surcharges', {
            'fields': ('temp_control_surcharge', 'signature_required_surcharge', 'rush_delivery_surcharge', 'other_surcharges')
        }),
        ('Discounts', {
            'fields': ('discount_percentage', 'discount_amount')
        }),
        ('Tax & Total', {
            'fields': ('tax_percentage', 'tax_amount', 'subtotal', 'total_cost')
        }),
        ('Metadata', {
            'fields': ('currency', 'notes', 'calculated_at', 'updated_at')
        }),
    )
