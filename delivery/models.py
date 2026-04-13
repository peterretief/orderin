from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser, ServiceAgent
from orders.models import Order


class ColdChainRequirement(models.Model):
    """
    Specifies temperature and storage requirements for products/orders.
    Can be applied at product level or order level.
    """
    
    TEMPERATURE_UNIT_CHOICES = (
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    )
    
    STORAGE_TYPE_CHOICES = (
        ('frozen', 'Frozen (-18°C or below)'),
        ('refrigerated', 'Refrigerated (2-8°C)'),
        ('ambient', 'Ambient (15-25°C)'),
        ('dry', 'Dry Storage (no moisture)'),
    )
    
    product = models.ForeignKey(
        'market.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cold_chain_requirements'
    )
    name = models.CharField(max_length=255)
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2)
    temperature_unit = models.CharField(max_length=1, choices=TEMPERATURE_UNIT_CHOICES, default='C')
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES)
    max_humidity_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    requires_insulation = models.BooleanField(default=False)
    requires_ice_packs = models.BooleanField(default=False)
    max_delivery_hours = models.IntegerField(null=True, blank=True, help_text="Maximum hours from pickup to delivery")
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} ({self.storage_type})'
    
    class Meta:
        verbose_name = 'Cold Chain Requirement'
        verbose_name_plural = 'Cold Chain Requirements'


class DeliveryVehicle(models.Model):
    """Tracks vehicle specifications and cold chain capabilities."""
    
    TEMPERATURE_UNIT_CHOICES = (
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    )
    
    service_agent = models.ForeignKey(
        ServiceAgent,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    vehicle_type = models.CharField(
        max_length=100,
        help_text="e.g., Car, Motorcycle, Truck, Bike"
    )
    registration_number = models.CharField(max_length=50, unique=True)
    vehicle_make_model = models.CharField(max_length=255, blank=True, null=True)
    max_weight_capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="in kg"
    )
    max_volume_capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="in liters"
    )
    
    # Temperature control
    has_temperature_control = models.BooleanField(
        default=False,
        help_text="Vehicle has refrigerated/insulated compartment"
    )
    min_temp_capability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_temp_capability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    temperature_unit = models.CharField(
        max_length=1,
        choices=TEMPERATURE_UNIT_CHOICES,
        default='C'
    )
    
    # Sensors and tracking
    has_gps_tracking = models.BooleanField(default=False)
    has_temperature_sensor = models.BooleanField(default=False)
    has_humidity_sensor = models.BooleanField(default=False)
    
    # Maintenance
    maintenance_due_date = models.DateField(null=True, blank=True)
    last_sanitization_date = models.DateField(null=True, blank=True)
    last_temperature_calibration = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.vehicle_type} - {self.registration_number} ({self.service_agent.user.service_name})'
    
    class Meta:
        verbose_name = 'Delivery Vehicle'
        verbose_name_plural = 'Delivery Vehicles'


class DeliveryMethod(models.Model):
    """Delivery options available to customers."""
    
    METHOD_TYPE_CHOICES = (
        ('collection', 'Customer Collection'),
        ('delivery', 'Home Delivery'),
        ('collection_point', 'Collection Point'),
    )
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} ({self.get_method_type_display()})'
    
    class Meta:
        verbose_name = 'Delivery Method'
        verbose_name_plural = 'Delivery Methods'


class CollectionPoint(models.Model):
    """Third-party locations where orders can be collected."""
    
    LOCATION_TYPE_CHOICES = (
        ('shop', 'Shop'),
        ('home', 'Home'),
        ('community_center', 'Community Center'),
        ('office', 'Office'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=255)
    owner_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='collection_points'
    )
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    
    operating_hours_start = models.TimeField()
    operating_hours_end = models.TimeField()
    
    max_storage_capacity = models.IntegerField(help_text="Maximum orders that can be stored")
    current_orders_count = models.IntegerField(default=0)
    has_temperature_control = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} ({self.city})'
    
    class Meta:
        verbose_name = 'Collection Point'
        verbose_name_plural = 'Collection Points'


class OrderDelivery(models.Model):
    """Links orders to delivery details and tracks delivery progress."""
    
    DELIVERY_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('collected', 'Collected by Customer'),
        ('cancelled', 'Cancelled'),
        ('at_collection_point', 'At Collection Point'),
    )
    
    COLD_CHAIN_COMPLIANCE_CHOICES = (
        ('compliant', 'Compliant'),
        ('warning', 'Warning - Minor Deviation'),
        ('breach', 'Breach - Out of Spec'),
        ('unchecked', 'Not Monitored'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT)
    
    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='pending'
    )
    
    delivery_date = models.DateField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # For home delivery
    delivery_address = models.TextField(null=True, blank=True)
    delivery_city = models.CharField(max_length=100, null=True, blank=True)
    delivery_state = models.CharField(max_length=100, null=True, blank=True)
    delivery_zip_code = models.CharField(max_length=20, null=True, blank=True)
    
    # For collection point delivery
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    
    # Distance and cost tracking
    delivery_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance in kilometers from store to delivery address"
    )
    
    # Cold chain
    cold_chain_requirement = models.ForeignKey(
        ColdChainRequirement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_deliveries'
    )
    
    cold_chain_compliance = models.CharField(
        max_length=20,
        choices=COLD_CHAIN_COMPLIANCE_CHOICES,
        default='unchecked'
    )
    cold_chain_compliance_notes = models.TextField(blank=True, null=True)
    
    delivery_notes = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    signature_required = models.BooleanField(default=False)
    proof_of_delivery = models.ImageField(
        upload_to='delivery/proof/',
        null=True,
        blank=True
    )
    
    total_hours_in_transit = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Delivery for Order #{self.order.id} - {self.get_delivery_status_display()}'
    
    class Meta:
        verbose_name = 'Order Delivery'
        verbose_name_plural = 'Order Deliveries'


class DeliveryTracking(models.Model):
    """Real-time tracking of order transportation with environmental conditions."""
    
    TEMPERATURE_UNIT_CHOICES = (
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    )
    
    TEMPERATURE_STATUS_CHOICES = (
        ('optimal', 'Optimal'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )
    
    delivery_assignment = models.OneToOneField(
        'DeliveryAssignment',
        on_delete=models.CASCADE,
        related_name='tracking_data'  # Changed related_name to avoid clash
    )
    
    # Location
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_description = models.CharField(max_length=255, blank=True, null=True)
    gps_accuracy = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    
    # Temperature monitoring
    current_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_unit = models.CharField(max_length=1, choices=TEMPERATURE_UNIT_CHOICES, default='C')
    temperature_deviation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ambient_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    vehicle_temperature_status = models.CharField(
        max_length=20,
        choices=TEMPERATURE_STATUS_CHOICES,
        default='optimal'
    )
    
    # Device status
    battery_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Battery percentage"
    )
    signal_strength = models.IntegerField(null=True, blank=True, help_text="Signal strength percentage")
    
    tracked_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Tracking for {self.delivery_assignment}'
    
    class Meta:
        verbose_name = 'Delivery Tracking'
        verbose_name_plural = 'Delivery Trackings'


class DeliveryTrackingEvent(models.Model):
    """Immutable audit log of all tracking events."""
    
    EVENT_TYPE_CHOICES = (
        ('temperature_reading', 'Temperature Reading'),
        ('location_update', 'Location Update'),
        ('deviation_detected', 'Deviation Detected'),
        ('system_breach', 'System Breach'),
        ('manual_entry', 'Manual Entry'),
        ('status_change', 'Status Change'),
        ('sensor_failure', 'Sensor Failure'),
        ('door_opened', 'Fridge Door Opened'),
    )
    
    SEVERITY_CHOICES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )
    
    delivery_tracking = models.ForeignKey(
        DeliveryTracking,
        on_delete=models.CASCADE,
        related_name='tracking_events'
    )
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    event_description = models.TextField()
    
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    event_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='info')
    requires_action = models.BooleanField(default=False)
    
    action_taken = models.TextField(blank=True, null=True)
    action_taken_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_actions'
    )
    action_taken_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.get_event_type_display()} - {self.event_severity.upper()}'
    
    class Meta:
        verbose_name = 'Delivery Tracking Event'
        verbose_name_plural = 'Delivery Tracking Events'
        ordering = ['-created_at']


class DeliveryAssignment(models.Model):
    """Assigns delivery agents and vehicles to orders."""
    
    ASSIGNMENT_STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    SUITABILITY_CHOICES = (
        ('suitable', 'Suitable'),
        ('marginal', 'Marginal'),
        ('unsuitable', 'Unsuitable'),
    )
    
    order_delivery = models.ForeignKey(OrderDelivery, on_delete=models.CASCADE, related_name='assignments')
    delivery_agent = models.ForeignKey(ServiceAgent, on_delete=models.CASCADE, related_name='delivery_assignments')
    
    assigned_vehicle = models.ForeignKey(
        DeliveryVehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments'
    )
    
    delivery_tracking = models.ForeignKey(
        DeliveryTracking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments'
    )
    
    assignment_status = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_STATUS_CHOICES,
        default='assigned'
    )
    
    vehicle_suitability_check = models.CharField(
        max_length=20,
        choices=SUITABILITY_CHOICES,
        null=True,
        blank=True
    )
    vehicle_suitability_notes = models.TextField(blank=True, null=True)
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    cold_chain_monitoring_enabled = models.BooleanField(default=True)
    monitoring_frequency_minutes = models.IntegerField(default=15)
    
    pickup_time = models.DateTimeField(null=True, blank=True)
    last_sensor_reading_time = models.DateTimeField(null=True, blank=True)
    compliance_check_passed = models.BooleanField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Assignment #{self.id} - {self.delivery_agent.user.service_name} for Order #{self.order_delivery.order.id}'
    
    class Meta:
        verbose_name = 'Delivery Assignment'
        verbose_name_plural = 'Delivery Assignments'
        unique_together = ('order_delivery', 'delivery_agent')


class DeliveryComplianceReport(models.Model):
    """
    Summary compliance report for completed deliveries.
    Generated at delivery completion for cold chain verification.
    """
    
    delivery_assignment = models.OneToOneField(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='compliance_report'
    )
    
    total_deviations = models.IntegerField(default=0)
    max_temperature_deviation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    min_temperature_deviation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    critical_events_count = models.IntegerField(default=0)
    warning_events_count = models.IntegerField(default=0)
    
    compliance_status = models.CharField(
        max_length=20,
        choices=[
            ('pass', 'Pass'),
            ('warning', 'Warning'),
            ('fail', 'Fail'),
        ]
    )
    
    compliance_notes = models.TextField(blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Compliance Report for {self.delivery_assignment}'
    
    class Meta:
        verbose_name = 'Delivery Compliance Report'
        verbose_name_plural = 'Delivery Compliance Reports'


class DeliveryLocationHistory(models.Model):
    """
    Historical GPS tracking points for delivery.
    Records every location update during delivery for route reconstruction.
    """
    
    delivery_assignment = models.ForeignKey(
        DeliveryAssignment,
        on_delete=models.CASCADE,
        related_name='location_history'
    )
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_address = models.CharField(max_length=500, blank=True, null=True)
    
    accuracy = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="GPS accuracy in meters"
    )
    altitude = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Altitude in meters"
    )
    speed = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Speed in km/h"
    )
    bearing = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Direction in degrees"
    )
    
    battery_percentage = models.IntegerField(null=True, blank=True)
    signal_strength = models.IntegerField(null=True, blank=True)
    
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Location for {self.delivery_assignment} at {self.recorded_at}'
    
    class Meta:
        verbose_name = 'Delivery Location History'
        verbose_name_plural = 'Delivery Location Histories'
        ordering = ['recorded_at']
        indexes = [
            models.Index(fields=['delivery_assignment', 'recorded_at']),
        ]


class DeliveryRoute(models.Model):
    """
    Planned route for a delivery agent with multiple stops.
    Optimized sequence of deliveries for the day.
    """
    
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    delivery_agent = models.ForeignKey(
        ServiceAgent,
        on_delete=models.CASCADE,
        related_name='delivery_routes'
    )
    assigned_vehicle = models.ForeignKey(
        DeliveryVehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    route_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Route details
    total_deliveries = models.IntegerField(default=0)
    completed_deliveries = models.IntegerField(default=0)
    total_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total planned distance in km"
    )
    estimated_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Estimated time to complete route"
    )
    actual_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Actual time taken to complete route"
    )
    actual_distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual distance traveled"
    )
    
    # Pickup/dropoff points
    start_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Route for {self.delivery_agent.user.service_name} on {self.route_date}'
    
    class Meta:
        verbose_name = 'Delivery Route'
        verbose_name_plural = 'Delivery Routes'
        ordering = ['-route_date']


class RouteStop(models.Model):
    """
    Individual stop/delivery on a route in optimized sequence.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reached', 'Reached'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    )
    
    delivery_route = models.ForeignKey(
        DeliveryRoute,
        on_delete=models.CASCADE,
        related_name='stops'
    )
    delivery_assignment = models.OneToOneField(
        DeliveryAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='route_stop'
    )
    
    sequence = models.IntegerField(help_text="Order in the route (1, 2, 3, ...)")
    
    destination_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    destination_address = models.CharField(max_length=500)
    destination_name = models.CharField(max_length=255, blank=True, null=True)
    
    distance_from_previous_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    estimated_arrival_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_time = models.DateTimeField(null=True, blank=True)
    service_time_minutes = models.IntegerField(null=True, blank=True)
    actual_service_time_minutes = models.IntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Stop #{self.sequence} - {self.destination_name or self.destination_address}'
    
    class Meta:
        verbose_name = 'Route Stop'
        verbose_name_plural = 'Route Stops'
        ordering = ['delivery_route', 'sequence']
        unique_together = ('delivery_route', 'sequence')


class RoutePlanningSetting(models.Model):
    """
    Settings for route optimization algorithm.
    """
    
    ALGORITHM_CHOICES = (
        ('nearest_neighbor', 'Nearest Neighbor'),
        ('tsp', 'Traveling Salesman'),
        ('genetic', 'Genetic Algorithm'),
        ('custom', 'Custom'),
    )
    
    service_agent = models.OneToOneField(
        ServiceAgent,
        on_delete=models.CASCADE,
        related_name='route_planning_settings'
    )
    
    optimization_algorithm = models.CharField(
        max_length=20,
        choices=ALGORITHM_CHOICES,
        default='nearest_neighbor'
    )
    
    max_deliveries_per_day = models.IntegerField(default=20)
    max_route_duration_hours = models.DecimalField(max_digits=4, decimal_places=1, default=8)
    max_weight_per_route = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    consider_time_windows = models.BooleanField(default=True)
    consider_vehicle_capacity = models.BooleanField(default=True)
    avoid_traffic = models.BooleanField(default=True)
    
    prefer_faster_routes = models.BooleanField(default=True)
    prefer_shorter_routes = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Route planning settings for {self.service_agent.user.service_name}'
    
    class Meta:
        verbose_name = 'Route Planning Setting'
        verbose_name_plural = 'Route Planning Settings'


class DeliveryPricingTier(models.Model):
    """Base pricing structure for delivery methods with distance-based tiers."""
    
    DISTANCE_UNIT_CHOICES = (
        ('km', 'Kilometers'),
        ('miles', 'Miles'),
    )
    
    delivery_method = models.ForeignKey(
        DeliveryMethod,
        on_delete=models.CASCADE,
        related_name='pricing_tiers'
    )
    
    # Distance range
    distance_unit = models.CharField(
        max_length=10,
        choices=DISTANCE_UNIT_CHOICES,
        default='km'
    )
    min_distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Minimum distance for this tier"
    )
    max_distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Maximum distance for this tier. Use 999999 for unlimited"
    )
    
    # Base cost
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base price for this distance tier"
    )
    
    # Per-unit costs
    price_per_unit_distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Additional cost per km/mile"
    )
    
    price_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Additional cost per kilogram (optional)"
    )
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.delivery_method.name} - {self.min_distance}-{self.max_distance}{self.distance_unit}'
    
    class Meta:
        verbose_name = 'Delivery Pricing Tier'
        verbose_name_plural = 'Delivery Pricing Tiers'
        ordering = ['delivery_method', 'min_distance']
        unique_together = ['delivery_method', 'min_distance', 'max_distance']


class WeightBasedPricing(models.Model):
    """Weight-based pricing surcharges for oversized or heavy items."""
    
    min_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Minimum weight in kg for this surcharge"
    )
    max_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Maximum weight in kg. Use 999999 for unlimited"
    )
    
    surcharge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Surcharge %",
        help_text="Percentage surcharge on base price"
    )
    
    surcharge_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Fixed amount surcharge"
    )
    
    applies_to_all_methods = models.BooleanField(
        default=True,
        help_text="If False, select specific delivery methods below"
    )
    
    delivery_methods = models.ManyToManyField(
        DeliveryMethod,
        blank=True,
        related_name='weight_pricing',
        help_text="Select specific methods if not applying to all"
    )
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.min_weight_kg}-{self.max_weight_kg}kg surcharge'
    
    class Meta:
        verbose_name = 'Weight-Based Pricing'
        verbose_name_plural = 'Weight-Based Pricing'
        ordering = ['min_weight_kg']


class TempControlPricing(models.Model):
    """Temperature control surcharges based on cold chain requirements."""
    
    STORAGE_TYPE_CHOICES = (
        ('frozen', 'Frozen (-18°C or below)'),
        ('refrigerated', 'Refrigerated (2-8°C)'),
        ('ambient', 'Ambient (15-25°C)'),
        ('dry', 'Dry Storage'),
    )
    
    storage_type = models.CharField(
        max_length=20,
        choices=STORAGE_TYPE_CHOICES,
        unique=True
    )
    
    surcharge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage surcharge on base price"
    )
    
    surcharge_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Fixed amount surcharge"
    )
    
    requires_vehicle_capability = models.BooleanField(
        default=True,
        help_text="Only available with temperature-controlled vehicles"
    )
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.get_storage_type_display()} surcharge'
    
    class Meta:
        verbose_name = 'Temperature Control Pricing'
        verbose_name_plural = 'Temperature Control Pricing'


class DeliveryCost(models.Model):
    """Calculated delivery cost breakdown for an order delivery."""
    
    order_delivery = models.OneToOneField(
        OrderDelivery,
        on_delete=models.CASCADE,
        related_name='cost_breakdown'
    )
    
    # Cost components
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base price from pricing tier"
    )
    
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Delivery distance in km"
    )
    
    distance_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional charge based on distance"
    )
    
    actual_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual weight of items"
    )
    
    weight_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Surcharge for heavy items"
    )
    
    temp_control_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Temperature control surcharge"
    )
    
    # Optional surcharges
    signature_required_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Additional charge if signature required"
    )
    
    rush_delivery_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Rush/urgent delivery surcharge"
    )
    
    other_surcharges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Any other additional charges"
    )
    
    # Discounts
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage discount"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Fixed amount discount"
    )
    
    # Tax
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tax percentage"
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Calculated tax amount"
    )
    
    # Total
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total before tax"
    )
    
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total delivery cost including tax"
    )
    
    # Metadata
    currency = models.CharField(max_length=3, default='ZAR')
    notes = models.TextField(blank=True, null=True)
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_subtotal(self):
        """Calculate subtotal from all components."""
        subtotal = (
            self.base_price +
            self.distance_charge +
            self.weight_surcharge +
            self.temp_control_surcharge +
            self.signature_required_surcharge +
            self.rush_delivery_surcharge +
            self.other_surcharges -
            self.discount_amount
        )
        
        # Apply percentage discount if any
        if self.discount_percentage > 0:
            subtotal = subtotal * (1 - self.discount_percentage / 100)
        
        return max(subtotal, 0)  # Ensure not negative
    
    def calculate_total(self):
        """Calculate total including tax."""
        self.subtotal = self.calculate_subtotal()
        self.tax_amount = self.subtotal * (self.tax_percentage / 100) if self.tax_percentage > 0 else 0
        self.total_cost = self.subtotal + self.tax_amount
        return self.total_cost
    
    def __str__(self):
        return f'Delivery cost for Order #{self.order_delivery.order.id}: R{self.total_cost}'
    
    class Meta:
        verbose_name = 'Delivery Cost'
        verbose_name_plural = 'Delivery Costs'
