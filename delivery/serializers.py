from rest_framework import serializers
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


class ColdChainRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColdChainRequirement
        fields = [
            'id', 'product', 'name', 'min_temperature', 'max_temperature',
            'temperature_unit', 'storage_type', 'max_humidity_percentage',
            'requires_insulation', 'requires_ice_packs', 'max_delivery_hours', 'notes'
        ]


class DeliveryVehicleSerializer(serializers.ModelSerializer):
    service_agent_name = serializers.CharField(source='service_agent.user.service_name', read_only=True)
    
    class Meta:
        model = DeliveryVehicle
        fields = [
            'id', 'service_agent', 'service_agent_name', 'vehicle_type', 'registration_number',
            'vehicle_make_model', 'max_weight_capacity', 'max_volume_capacity',
            'has_temperature_control', 'min_temp_capability', 'max_temp_capability',
            'temperature_unit', 'has_gps_tracking', 'has_temperature_sensor',
            'has_humidity_sensor', 'maintenance_due_date', 'last_sanitization_date',
            'last_temperature_calibration', 'is_active'
        ]


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'name', 'code', 'description', 'method_type', 'is_active']


class CollectionPointSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner_user.username', read_only=True)
    
    class Meta:
        model = CollectionPoint
        fields = [
            'id', 'name', 'owner_user', 'owner_username', 'location_type', 'address',
            'city', 'state', 'zip_code', 'latitude', 'longitude', 'phone', 'email',
            'operating_hours_start', 'operating_hours_end', 'max_storage_capacity',
            'current_orders_count', 'has_temperature_control', 'is_active'
        ]


class DeliveryTrackingEventSerializer(serializers.ModelSerializer):
    action_taken_by_username = serializers.CharField(source='action_taken_by.username', read_only=True)
    
    class Meta:
        model = DeliveryTrackingEvent
        fields = [
            'id', 'delivery_tracking', 'event_type', 'event_description', 'temperature',
            'latitude', 'longitude', 'event_severity', 'requires_action', 'action_taken',
            'action_taken_by', 'action_taken_by_username', 'action_taken_at', 'created_at'
        ]


class DeliveryTrackingSerializer(serializers.ModelSerializer):
    tracking_events = DeliveryTrackingEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliveryTracking
        fields = [
            'id', 'delivery_assignment', 'current_latitude', 'current_longitude',
            'current_location_description', 'current_temperature', 'temperature_unit',
            'temperature_deviation', 'ambient_temperature', 'humidity_percentage',
            'vehicle_temperature_status', 'gps_accuracy', 'battery_level',
            'signal_strength', 'tracked_at', 'tracking_events'
        ]


class OrderDeliverySerializer(serializers.ModelSerializer):
    delivery_method_name = serializers.CharField(source='delivery_method.name', read_only=True)
    collection_point_name = serializers.CharField(source='collection_point.name', read_only=True)
    cold_chain_requirement_name = serializers.CharField(source='cold_chain_requirement.name', read_only=True)
    
    class Meta:
        model = OrderDelivery
        fields = [
            'id', 'order', 'delivery_method', 'delivery_method_name', 'delivery_status',
            'delivery_date', 'estimated_delivery_time', 'actual_delivery_time',
            'delivery_address', 'delivery_city', 'delivery_state', 'delivery_zip_code',
            'collection_point', 'collection_point_name', 'cold_chain_requirement',
            'cold_chain_requirement_name', 'cold_chain_compliance',
            'cold_chain_compliance_notes', 'delivery_notes', 'special_instructions',
            'signature_required', 'proof_of_delivery', 'total_hours_in_transit'
        ]


class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    delivery_agent_name = serializers.CharField(source='delivery_agent.user.service_name', read_only=True)
    vehicle_info = DeliveryVehicleSerializer(source='assigned_vehicle', read_only=True)
    tracking_info = DeliveryTrackingSerializer(source='delivery_tracking', read_only=True)
    order_id = serializers.IntegerField(source='order_delivery.order.id', read_only=True)
    
    class Meta:
        model = DeliveryAssignment
        fields = [
            'id', 'order_delivery', 'order_id', 'delivery_agent', 'delivery_agent_name',
            'assigned_vehicle', 'vehicle_info', 'delivery_tracking', 'tracking_info',
            'assignment_status', 'vehicle_suitability_check', 'vehicle_suitability_notes',
            'assigned_at', 'accepted_at', 'started_at', 'completed_at', 'delivery_fee',
            'cold_chain_monitoring_enabled', 'monitoring_frequency_minutes', 'pickup_time',
            'last_sensor_reading_time', 'compliance_check_passed', 'notes'
        ]
        read_only_fields = ['assigned_at', 'created_at', 'updated_at']


class DeliveryComplianceReportSerializer(serializers.ModelSerializer):
    delivery_agent_name = serializers.CharField(
        source='delivery_assignment.delivery_agent.user.service_name',
        read_only=True
    )
    
    class Meta:
        model = DeliveryComplianceReport
        fields = [
            'id', 'delivery_assignment', 'delivery_agent_name', 'total_deviations',
            'max_temperature_deviation', 'min_temperature_deviation', 'critical_events_count',
            'warning_events_count', 'compliance_status', 'compliance_notes', 'generated_at'
        ]


class DeliveryLocationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocationHistory
        fields = [
            'id', 'delivery_assignment', 'latitude', 'longitude', 'location_address',
            'accuracy', 'altitude', 'speed', 'bearing', 'battery_percentage',
            'signal_strength', 'temperature', 'humidity', 'recorded_at'
        ]


class RouteStopSerializer(serializers.ModelSerializer):
    delivery_method = serializers.CharField(source='delivery_assignment.order_delivery.delivery_method.name', read_only=True)
    customer_address = serializers.CharField(source='delivery_assignment.order_delivery.delivery_address', read_only=True)
    
    class Meta:
        model = RouteStop
        fields = [
            'id', 'delivery_route', 'delivery_assignment', 'sequence',
            'destination_latitude', 'destination_longitude', 'destination_address',
            'destination_name', 'distance_from_previous_km', 'estimated_arrival_time',
            'actual_arrival_time', 'service_time_minutes', 'actual_service_time_minutes',
            'status', 'delivery_method', 'customer_address'
        ]


class DeliveryRouteSerializer(serializers.ModelSerializer):
    delivery_agent_name = serializers.CharField(source='delivery_agent.user.service_name', read_only=True)
    vehicle_info = DeliveryVehicleSerializer(source='assigned_vehicle', read_only=True)
    stops = RouteStopSerializer(many=True, read_only=True)
    
    class Meta:
        model = DeliveryRoute
        fields = [
            'id', 'delivery_agent', 'delivery_agent_name', 'assigned_vehicle', 'vehicle_info',
            'route_date', 'status', 'total_deliveries', 'completed_deliveries',
            'total_distance_km', 'estimated_duration_minutes', 'actual_duration_minutes',
            'actual_distance_km', 'start_latitude', 'start_longitude', 'end_latitude',
            'end_longitude', 'notes', 'started_at', 'completed_at', 'stops'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RoutePlanningSettingSerializer(serializers.ModelSerializer):
    service_agent_name = serializers.CharField(source='service_agent.user.service_name', read_only=True)
    
    class Meta:
        model = RoutePlanningSetting
        fields = [
            'id', 'service_agent', 'service_agent_name', 'optimization_algorithm',
            'max_deliveries_per_day', 'max_route_duration_hours', 'max_weight_per_route',
            'consider_time_windows', 'consider_vehicle_capacity', 'avoid_traffic',
            'prefer_faster_routes', 'prefer_shorter_routes', 'notes'
        ]


class DeliveryPricingTierSerializer(serializers.ModelSerializer):
    delivery_method_name = serializers.CharField(source='delivery_method.name', read_only=True)
    
    class Meta:
        model = DeliveryPricingTier
        fields = [
            'id', 'delivery_method', 'delivery_method_name', 'distance_unit',
            'min_distance', 'max_distance', 'base_price', 'price_per_unit_distance',
            'price_per_kg', 'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WeightBasedPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightBasedPricing
        fields = [
            'id', 'min_weight_kg', 'max_weight_kg', 'surcharge_percentage',
            'surcharge_fixed', 'applies_to_all_methods', 'delivery_methods',
            'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TempControlPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempControlPricing
        fields = [
            'id', 'storage_type', 'surcharge_percentage', 'surcharge_fixed',
            'requires_vehicle_capability', 'is_active', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DeliveryCostSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(source='order_delivery.order.id', read_only=True)
    method_name = serializers.CharField(source='order_delivery.delivery_method.name', read_only=True)
    
    class Meta:
        model = DeliveryCost
        fields = [
            'id', 'order_delivery', 'order_id', 'method_name', 'base_price',
            'distance_km', 'distance_charge', 'actual_weight_kg', 'weight_surcharge',
            'temp_control_surcharge', 'signature_required_surcharge', 'rush_delivery_surcharge',
            'other_surcharges', 'discount_percentage', 'discount_amount', 'tax_percentage',
            'tax_amount', 'subtotal', 'total_cost', 'currency', 'notes',
            'calculated_at', 'updated_at'
        ]
        read_only_fields = ['calculated_at', 'updated_at', 'subtotal', 'total_cost', 'tax_amount']
