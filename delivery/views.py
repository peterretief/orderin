from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
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
)
from .serializers import (
    ColdChainRequirementSerializer,
    DeliveryVehicleSerializer,
    DeliveryMethodSerializer,
    CollectionPointSerializer,
    OrderDeliverySerializer,
    DeliveryTrackingSerializer,
    DeliveryTrackingEventSerializer,
    DeliveryAssignmentSerializer,
    DeliveryComplianceReportSerializer,
    DeliveryLocationHistorySerializer,
    DeliveryRouteSerializer,
    RouteStopSerializer,
    RoutePlanningSettingSerializer,
)


class ColdChainRequirementViewSet(viewsets.ModelViewSet):
    """API for cold chain requirements."""
    queryset = ColdChainRequirement.objects.all()
    serializer_class = ColdChainRequirementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'storage_type']


class DeliveryVehicleViewSet(viewsets.ModelViewSet):
    """API for delivery vehicles."""
    queryset = DeliveryVehicle.objects.all()
    serializer_class = DeliveryVehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['registration_number', 'vehicle_type']
    
    def get_queryset(self):
        """Filter to agent's own vehicles if not admin."""
        user = self.request.user
        if user.user_type == 'delivery_person':
            return DeliveryVehicle.objects.filter(service_agent__user=user)
        return DeliveryVehicle.objects.all()


class DeliveryMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """API for delivery methods (read-only for users)."""
    queryset = DeliveryMethod.objects.filter(is_active=True)
    serializer_class = DeliveryMethodSerializer
    permission_classes = [IsAuthenticated]


class CollectionPointViewSet(viewsets.ModelViewSet):
    """API for collection points."""
    queryset = CollectionPoint.objects.filter(is_active=True)
    serializer_class = CollectionPointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'location_type']
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get collection points near user's location."""
        city = request.query_params.get('city')
        if city:
            points = CollectionPoint.objects.filter(city=city, is_active=True)
            serializer = self.get_serializer(points, many=True)
            return Response(serializer.data)
        return Response({'error': 'City parameter required'}, status=status.HTTP_400_BAD_REQUEST)


class OrderDeliveryViewSet(viewsets.ModelViewSet):
    """API for order delivery management."""
    queryset = OrderDelivery.objects.all()
    serializer_class = OrderDeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on user type."""
        user = self.request.user
        if user.user_type == 'subscriber':
            return OrderDelivery.objects.filter(order__subscriber=user)
        elif user.user_type == 'delivery_person':
            return OrderDelivery.objects.filter(
                assignments__delivery_agent__user=user
            ).distinct()
        return OrderDelivery.objects.all()
    
    @action(detail=True, methods=['post'])
    def update_delivery_method(self, request, pk=None):
        """Update delivery method for an order."""
        order_delivery = self.get_object()
        method_id = request.data.get('delivery_method_id')
        
        if not method_id:
            return Response(
                {'error': 'delivery_method_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order_delivery.delivery_method_id = method_id
        order_delivery.save()
        serializer = self.get_serializer(order_delivery)
        return Response(serializer.data)


class DeliveryTrackingViewSet(viewsets.ModelViewSet):
    """API for delivery tracking."""
    queryset = DeliveryTracking.objects.all()
    serializer_class = DeliveryTrackingSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_tracking(self, request):
        """Create or update tracking for a delivery assignment."""
        assignment_id = request.data.get('delivery_assignment_id')
        
        if not assignment_id:
            return Response(
                {'error': 'delivery_assignment_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment = get_object_or_404(DeliveryAssignment, id=assignment_id)
        
        # Check if tracking exists
        tracking, created = DeliveryTracking.objects.get_or_create(
            delivery_assignment=assignment
        )
        
        # Update fields
        if 'current_latitude' in request.data:
            tracking.current_latitude = request.data['current_latitude']
        if 'current_longitude' in request.data:
            tracking.current_longitude = request.data['current_longitude']
        if 'current_temperature' in request.data:
            tracking.current_temperature = request.data['current_temperature']
        if 'humidity_percentage' in request.data:
            tracking.humidity_percentage = request.data['humidity_percentage']
        if 'current_location_description' in request.data:
            tracking.current_location_description = request.data['current_location_description']
        
        tracking.save()
        serializer = self.get_serializer(tracking)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class DeliveryTrackingEventViewSet(viewsets.ModelViewSet):
    """API for delivery tracking events."""
    queryset = DeliveryTrackingEvent.objects.all()
    serializer_class = DeliveryTrackingEventSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Create a tracking event."""
        event = DeliveryTrackingEvent.objects.create(
            delivery_tracking_id=request.data.get('delivery_tracking_id'),
            event_type=request.data.get('event_type'),
            event_description=request.data.get('event_description'),
            temperature=request.data.get('temperature'),
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude'),
            event_severity=request.data.get('event_severity', 'info'),
            requires_action=request.data.get('requires_action', False),
        )
        serializer = self.get_serializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeliveryAssignmentViewSet(viewsets.ModelViewSet):
    """API for delivery assignments."""
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on user type."""
        user = self.request.user
        if user.user_type == 'delivery_person':
            return DeliveryAssignment.objects.filter(delivery_agent__user=user)
        return DeliveryAssignment.objects.all()
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a delivery assignment."""
        assignment = self.get_object()
        
        if assignment.assignment_status != 'assigned':
            return Response(
                {'error': f'Cannot accept assignment in {assignment.assignment_status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.assignment_status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a delivery assignment."""
        assignment = self.get_object()
        
        if assignment.assignment_status != 'assigned':
            return Response(
                {'error': f'Cannot reject assignment in {assignment.assignment_status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.assignment_status = 'rejected'
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_delivery(self, request, pk=None):
        """Mark delivery as in-progress."""
        assignment = self.get_object()
        
        if assignment.assignment_status not in ['accepted', 'assigned']:
            return Response(
                {'error': f'Cannot start delivery in {assignment.assignment_status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.assignment_status = 'in_progress'
        assignment.started_at = timezone.now()
        assignment.pickup_time = timezone.now()
        assignment.save()
        
        # Update order delivery status
        assignment.order_delivery.delivery_status = 'in_transit'
        assignment.order_delivery.save()
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_delivery(self, request, pk=None):
        """Mark delivery as completed."""
        assignment = self.get_object()
        
        if assignment.assignment_status != 'in_progress':
            return Response(
                {'error': f'Cannot complete delivery in {assignment.assignment_status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.assignment_status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()
        
        # Update order delivery status
        order_delivery = assignment.order_delivery
        order_delivery.delivery_status = 'delivered'
        order_delivery.actual_delivery_time = timezone.now()
        
        # Calculate hours in transit
        if assignment.pickup_time:
            hours_delta = (timezone.now() - assignment.pickup_time).total_seconds() / 3600
            order_delivery.total_hours_in_transit = int(hours_delta)
        
        order_delivery.save()
        
        # Generate compliance report if cold chain was monitored
        if assignment.cold_chain_monitoring_enabled and assignment.delivery_tracking:
            DeliveryComplianceReport.objects.get_or_create(
                delivery_assignment=assignment,
                defaults={
                    'compliance_status': 'pass',
                    'compliance_notes': 'Auto-generated on delivery completion'
                }
            )
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get current user's delivery assignments."""
        queryset = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(assignment_status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending assignments awaiting acceptance."""
        assignments = self.get_queryset().filter(assignment_status='assigned')
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class DeliveryComplianceReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing compliance reports."""
    queryset = DeliveryComplianceReport.objects.all()
    serializer_class = DeliveryComplianceReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on user type."""
        user = self.request.user
        if user.user_type == 'delivery_person':
            return DeliveryComplianceReport.objects.filter(
                delivery_assignment__delivery_agent__user=user
            )
        return DeliveryComplianceReport.objects.all()


class DeliveryLocationHistoryViewSet(viewsets.ModelViewSet):
    """API for location tracking history."""
    queryset = DeliveryLocationHistory.objects.all()
    serializer_class = DeliveryLocationHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['delivery_assignment__order_delivery__order__id']
    
    def get_queryset(self):
        """Filter based on user type."""
        user = self.request.user
        if user.user_type == 'delivery_person':
            return DeliveryLocationHistory.objects.filter(
                delivery_assignment__delivery_agent__user=user
            )
        return DeliveryLocationHistory.objects.all()
    
    @action(detail=False, methods=['post'])
    def record_location(self, request):
        """Record current location with tracking data."""
        assignment_id = request.data.get('delivery_assignment_id')
        
        if not assignment_id:
            return Response(
                {'error': 'delivery_assignment_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment = get_object_or_404(DeliveryAssignment, id=assignment_id)
        
        location = DeliveryLocationHistory.objects.create(
            delivery_assignment=assignment,
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude'),
            location_address=request.data.get('location_address'),
            accuracy=request.data.get('accuracy'),
            altitude=request.data.get('altitude'),
            speed=request.data.get('speed'),
            bearing=request.data.get('bearing'),
            battery_percentage=request.data.get('battery_percentage'),
            signal_strength=request.data.get('signal_strength'),
            temperature=request.data.get('temperature'),
            humidity=request.data.get('humidity'),
        )
        
        serializer = self.get_serializer(location)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def assignment_track(self, request):
        """Get location history for a specific assignment."""
        assignment_id = request.query_params.get('assignment_id')
        
        if not assignment_id:
            return Response(
                {'error': 'assignment_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = DeliveryLocationHistory.objects.filter(
            delivery_assignment_id=assignment_id
        ).order_by('recorded_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class DeliveryRouteViewSet(viewsets.ModelViewSet):
    """API for delivery route management."""
    queryset = DeliveryRoute.objects.all()
    serializer_class = DeliveryRouteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter routes by agent or date."""
        user = self.request.user
        queryset = DeliveryRoute.objects.all()
        
        if user.user_type == 'delivery_person':
            queryset = queryset.filter(delivery_agent__user=user)
        
        # Filter by date if provided
        date_filter = self.request.query_params.get('date')
        if date_filter:
            queryset = queryset.filter(route_date=date_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def start_route(self, request, pk=None):
        """Mark route as in-progress."""
        route = self.get_object()
        
        if route.status != 'planned':
            return Response(
                {'error': f'Cannot start route in {route.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route.status = 'in_progress'
        route.started_at = timezone.now()
        route.save()
        
        serializer = self.get_serializer(route)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_route(self, request, pk=None):
        """Mark route as completed."""
        route = self.get_object()
        
        if route.status != 'in_progress':
            return Response(
                {'error': f'Cannot complete route in {route.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route.status = 'completed'
        route.completed_at = timezone.now()
        route.completed_deliveries = route.stops.filter(status='completed').count()
        route.save()
        
        serializer = self.get_serializer(route)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def optimize_route(self, request):
        """Generate optimized route for deliveries."""
        date_param = request.data.get('date')
        agent_id = request.data.get('agent_id')
        vehicle_id = request.data.get('vehicle_id')
        
        if not all([date_param, agent_id]):
            return Response(
                {'error': 'date and agent_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get route
        route, created = DeliveryRoute.objects.get_or_create(
            delivery_agent_id=agent_id,
            route_date=date_param,
            defaults={
                'assigned_vehicle_id': vehicle_id,
                'status': 'planned'
            }
        )
        
        # Get assignments for this agent and date
        assignments = DeliveryAssignment.objects.filter(
            delivery_agent_id=agent_id,
            assigned_at__date=date_param,
            assignment_status__in=['assigned', 'accepted']
        )
        
        # Create stops in optimized order
        for idx, assignment in enumerate(assignments, 1):
            RouteStop.objects.get_or_create(
                delivery_route=route,
                delivery_assignment=assignment,
                defaults={
                    'sequence': idx,
                    'destination_latitude': assignment.order_delivery.delivery_latitude or 0,
                    'destination_longitude': assignment.order_delivery.delivery_longitude or 0,
                    'destination_address': assignment.order_delivery.delivery_address or 'TBD',
                }
            )
        
        route.total_deliveries = assignments.count()
        route.save()
        
        serializer = self.get_serializer(route)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RouteStopViewSet(viewsets.ModelViewSet):
    """API for route stops."""
    queryset = RouteStop.objects.all()
    serializer_class = RouteStopSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def mark_reached(self, request, pk=None):
        """Mark stop as reached."""
        stop = self.get_object()
        
        stop.status = 'reached'
        stop.actual_arrival_time = timezone.now()
        stop.save()
        
        serializer = self.get_serializer(stop)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark stop as completed."""
        stop = self.get_object()
        
        if stop.actual_arrival_time:
            actual_service_time = (timezone.now() - stop.actual_arrival_time).total_seconds() / 60
            stop.actual_service_time_minutes = int(actual_service_time)
        
        stop.status = 'completed'
        stop.save()
        
        # Update route progress
        route = stop.delivery_route
        route.completed_deliveries = route.stops.filter(status='completed').count()
        route.save()
        
        serializer = self.get_serializer(stop)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def route_stops(self, request):
        """Get all stops for a route in sequence."""
        route_id = request.query_params.get('route_id')
        
        if not route_id:
            return Response(
                {'error': 'route_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stops = RouteStop.objects.filter(delivery_route_id=route_id).order_by('sequence')
        serializer = self.get_serializer(stops, many=True)
        return Response(serializer.data)


class RoutePlanningSettingViewSet(viewsets.ModelViewSet):
    """API for route planning settings."""
    queryset = RoutePlanningSetting.objects.all()
    serializer_class = RoutePlanningSettingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter settings by agent."""
        user = self.request.user
        if user.user_type == 'delivery_person':
            return RoutePlanningSetting.objects.filter(service_agent__user=user)
        return RoutePlanningSetting.objects.all()
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """Get current agent's planning settings."""
        user = self.request.user
        
        if user.user_type != 'delivery_person':
            return Response(
                {'error': 'Only delivery persons can access this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            service_agent = user.service_profile
            settings = RoutePlanningSetting.objects.get(service_agent=service_agent)
            serializer = self.get_serializer(settings)
            return Response(serializer.data)
        except RoutePlanningSetting.DoesNotExist:
            return Response(
                {'error': 'No route planning settings found'},
                status=status.HTTP_404_NOT_FOUND
            )


# Additional API endpoints for checkout and customer-facing operations
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


@csrf_exempt
@require_http_methods(["POST"])
def calculate_delivery_cost(request):
    """Calculate delivery cost based on address and delivery method.
    
    Expected POST parameters:
    - delivery_method_id: ID of the delivery method
    - delivery_address: Street address
    - delivery_city: City name
    - store_address: Store address (optional, auto-calculated if not provided)
    - store_city: Store city (optional)
    
    Returns JSON with distance and cost breakdown.
    """
    import json
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    delivery_method_id = data.get('delivery_method_id')
    delivery_address = data.get('delivery_address')
    delivery_city = data.get('delivery_city')
    store_address = data.get('store_address')
    store_city = data.get('store_city', 'Cape Town')
    
    if not all([delivery_method_id, delivery_address, delivery_city]):
        return JsonResponse({
            'error': 'Missing required parameters: delivery_method_id, delivery_address, delivery_city'
        }, status=400)
    
    try:
        delivery_method = DeliveryMethod.objects.get(id=delivery_method_id, is_active=True)
    except DeliveryMethod.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid delivery method'
        }, status=404)
    
    # For collection point and regular collection, no distance calculation needed
    if delivery_method.name in ['collection_point', 'collection']:
        return JsonResponse({
            'method': delivery_method.name,
            'distance_km': 0,
            'base_fee': float(delivery_method.base_fee or 0),
            'total_cost': float(delivery_method.base_fee or 0),
            'currency': 'ZAR'
        })
    
    # For home delivery, calculate distance and cost
    if delivery_method.name == 'home_delivery':
        try:
            from delivery.distance import DeliveryDistanceAndCost
            import logging
            logger = logging.getLogger(__name__)
            
            # Use provided store address or default
            if not store_address:
                store_address = "Cape Town Market, Epping, Cape Town"
            else:
                store_address = f"{store_address}, {store_city}"
            
            delivery_full_address = f"{delivery_address}, {delivery_city}"
            
            # Validate addresses can be geocoded
            calc = DeliveryDistanceAndCost(store_address, delivery_full_address)
            
            # Check if store address can be geocoded
            store_coords = calc.geocode_address(store_address)
            if not store_coords:
                logger.warning(f"Could not geocode store address: {store_address}")
                return JsonResponse({
                    'error': f'Store location could not be found: {store_address}',
                    'address_issue': 'store',
                    'method': delivery_method.name,
                    'currency': 'ZAR'
                }, status=400)
            
            # Check if delivery address can be geocoded
            delivery_coords = calc.geocode_address(delivery_full_address)
            if not delivery_coords:
                logger.warning(f"Could not geocode delivery address: {delivery_full_address}")
                return JsonResponse({
                    'error': f'Delivery address could not be found. Please check the address format and include suburb/area name.',
                    'address_issue': 'delivery',
                    'method': delivery_method.name,
                    'currency': 'ZAR'
                }, status=400)
            
            # Both addresses are valid, calculate distance
            distance = calc.calculate_distance()
            
            if not distance:
                # Default to average distance if calculation fails
                distance = Decimal('15.0')
            
            # Get pricing tier for this distance
            from delivery.costing import DeliveryCostCalculator
            pricing_tier = delivery_method.pricing_tiers.first()
            
            if pricing_tier:
                base_fee = pricing_tier.base_fee
            else:
                base_fee = delivery_method.base_fee or Decimal('50.00')
            
            logger.info(f"Distance calculation successful: {store_address} → {delivery_full_address} = {distance} km")
            
            return JsonResponse({
                'method': delivery_method.name,
                'distance_km': float(distance),
                'base_fee': float(base_fee),
                'total_cost': float(base_fee),
                'estimate': True,
                'currency': 'ZAR',
                'success': True
            })
        except Exception as e:
            # If distance calculation fails, return error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating delivery cost: {e}")
            
            return JsonResponse({
                'method': delivery_method.name,
                'error': f'Unable to verify address. Please check your address format and try again.',
                'currency': 'ZAR'
            }, status=400)
    
    return JsonResponse({
        'error': 'Unknown delivery method'
    }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def validate_address(request):
    """Validate if an address can be geocoded.
    
    Expected POST parameters:
    - address: Full address string to validate
    
    Returns JSON with validation result.
    """
    import json
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'valid': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    
    address = data.get('address')
    
    if not address:
        return JsonResponse({
            'valid': False,
            'error': 'Missing address parameter'
        }, status=400)
    
    try:
        from delivery.distance import DeliveryDistanceAndCost
        import logging
        logger = logging.getLogger(__name__)
        
        # Create a temporary calculator to validate the address
        calc = DeliveryDistanceAndCost(address, "Observatory, Cape Town")
        
        # Check if address can be geocoded
        coords = calc.geocode_address(address)
        
        if coords:
            logger.info(f"Address validated successfully: {address} → {coords}")
            return JsonResponse({
                'valid': True,
                'address': address,
                'coordinates': {
                    'latitude': float(coords[0]),
                    'longitude': float(coords[1])
                }
            })
        else:
            logger.warning(f"Address could not be geocoded: {address}")
            return JsonResponse({
                'valid': False,
                'address': address,
                'error': 'Address not found. Please check the format and include suburb/area name.'
            })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error validating address {address}: {e}")
        
        return JsonResponse({
            'valid': False,
            'error': f'Error validating address: {str(e)[:100]}'
        }, status=400)
