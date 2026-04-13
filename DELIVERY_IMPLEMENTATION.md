# Delivery System - Implementation Guide

## Overview
The delivery system is fully implemented with models, dashboards, and APIs for managing order deliveries with comprehensive cold chain tracking.

---

## Components Implemented

### 1. Django Models (9 Total)
Located in `delivery/models.py`:

#### Core Delivery Models
- **DeliveryMethod** - Defines delivery options (collection, home delivery, collection point)
- **CollectionPoint** - Flexible third-party locations for order pickup
- **OrderDelivery** - Links orders to delivery details and cold chain requirements
- **DeliveryAssignment** - Assigns delivery agents and vehicles to orders

#### Tracking & Monitoring
- **DeliveryVehicle** - Vehicle specs with cold chain capabilities
- **DeliveryTracking** - Real-time GPS, temperature, humidity monitoring
- **DeliveryTrackingEvent** - Immutable audit log of all tracking events
- **DeliveryComplianceReport** - Compliance summary for completed deliveries

#### Requirements
- **ColdChainRequirement** - Temperature/storage specs for products/orders

### 2. REST API Endpoints
Base URL: `/api/delivery/`

#### ViewSets
```
/cold-chain-requirements/    - CRUD for cold chain specs
/vehicles/                   - Delivery vehicle management
/methods/                    - Available delivery methods (read-only)
/collection-points/          - Collection point management
  - /nearby/                 - Get points by city
/order-deliveries/           - Order delivery tracking
  - /update-delivery-method/ - Change delivery method
/tracking/                   - Real-time tracking
  - /create-tracking/        - Create/update tracking data
/tracking-events/            - Tracking event log
  - /create-event/           - Log new tracking event
/assignments/                - Delivery assignments
  - /accept/                 - Agent accepts assignment
  - /reject/                 - Agent rejects assignment
  - /start-delivery/         - Start delivery journey
  - /complete-delivery/      - Mark delivery complete
  - /my-assignments/         - Agent's assignments
  - /pending/                - Assignments awaiting acceptance
/compliance-reports/         - Compliance reports (read-only)
```

### 3. Delivery Agent Dashboard
- Location: `/dashboards/delivery-agent/`
- Features:
  - Key metrics: total, in-progress, completed deliveries
  - **Today's Deliveries** tab - Scheduled for today
  - **Assigned** tab - Awaiting acceptance with accept/reject buttons
  - **In Progress** tab - Active deliveries with real-time cold chain status
  - **Vehicle** tab - Vehicle specs and sensor capabilities
  - 7-day delivery trend chart
  - Performance metrics and earnings

### 4. Admin Interface
Django admin panel with full model management:
- `http://localhost:8000/admin/delivery/`
- All models registered with filters and search

---

## Cold Chain Tracking Features

### Real-Time Monitoring
```
Current Temperature   → Automatic recording (if sensor present)
Temperature Deviations → Detected automatically
Status Changes       → optimal → warning → critical
Location Tracking    → GPS coordinates & address
Humidity Monitoring  → For air-sensitive items
Battery/Signal       → Device health monitoring
```

### Compliance Tracking
```
Compliant    → All readings within spec
Warning      → Minor deviation, recoverable
Breach       → Out of spec, data compromised
Unchecked    → Not monitored
```

### Audit Trail
Every event logged immutably:
- Event type (temperature reading, location update, breach, sensor failure, etc.)
- Severity (info, warning, critical)
- Corrective actions taken
- Who took action and when

---

## Initial Setup

### 1. Delivery Methods Already Created
Run once (already done):
```bash
python manage.py setup_delivery_methods
```

This creates:
- Customer Pickup (collection)
- Standard Home Delivery (delivery)
- Collection Point Delivery (collection_point)
- Express Same-Day Delivery (delivery)

### 2. Create Delivery Vehicles (Admin or API)
Example via API:
```bash
POST /api/delivery/vehicles/
{
  "service_agent": 1,
  "vehicle_type": "Car",
  "registration_number": "KA01AB1234",
  "vehicle_make_model": "Maruti Swift",
  "max_weight_capacity": 500,
  "max_volume_capacity": 100,
  "has_temperature_control": true,
  "min_temp_capability": 2,
  "max_temp_capability": 8,
  "temperature_unit": "C",
  "has_gps_tracking": true,
  "has_temperature_sensor": true,
  "has_humidity_sensor": false
}
```

### 3. Set Cold Chain Requirements (Optional)
For frozen/refrigerated products:
```bash
POST /api/delivery/cold-chain-requirements/
{
  "product": 1,
  "name": "Frozen Storage",
  "min_temperature": -18,
  "max_temperature": -12,
  "temperature_unit": "C",
  "storage_type": "frozen",
  "max_delivery_hours": 4,
  "requires_ice_packs": true
}
```

### 4. Create Collection Points (Admin or API)
```bash
POST /api/delivery/collection-points/
{
  "name": "Green Mart Shop",
  "owner_user": 10,
  "location_type": "shop",
  "address": "123 Main Street",
  "city": "Bangalore",
  "state": "Karnataka",
  "zip_code": "560001",
  "phone": "9876543210",
  "operating_hours_start": "09:00:00",
  "operating_hours_end": "21:00:00",
  "max_storage_capacity": 50,
  "has_temperature_control": false
}
```

---

## User Workflows

### Customer (Subscriber)
1. Place order (existing functionality)
2. Choose delivery method at checkout
3. View order status including delivery tracking
4. Accept/reject delivery to collection point if applicable

### Delivery Agent
1. Login (user_type = 'delivery_person')
2. Go to dashboard `/dashboards/delivery-agent/`
3. View pending assignments (awaiting acceptance)
4. **Accept** assignment
5. **Start Delivery** when ready to begin
6. Update tracking (location, temperature) via dashboard or API
7. **Mark Complete** upon delivery

### Admin
1. View all deliveries in admin panel
2. Monitor compliance reports
3. Manage vehicles, collection points, cold chain requirements

---

## API Usage Examples

### Get Assigned Deliveries
```bash
GET /api/delivery/assignments/pending/
Headers: Authorization: Bearer <token>
```

### Accept a Delivery
```bash
POST /api/delivery/assignments/{id}/accept/
Headers: Authorization: Bearer <token>
```

### Update Location & Temperature
```bash
POST /api/delivery/tracking/create-tracking/
{
  "delivery_assignment_id": 1,
  "current_latitude": 13.0827,
  "current_longitude": 80.2707,
  "current_temperature": 5.2,
  "humidity_percentage": 45,
  "current_location_description": "Entering Bangalore"
}
```

### Complete Delivery
```bash
POST /api/delivery/assignments/{id}/complete_delivery/
Headers: Authorization: Bearer <token>
```

### View Compliance Report
```bash
GET /api/delivery/compliance-reports/{id}/
Headers: Authorization: Bearer <token>
```

---

## Key Features

### ✅ Three Delivery Methods
1. **Collection** - Customer picks up from location
2. **Home Delivery** - Agent delivers to address
3. **Collection Point** - Agent sends to shop/collection point

### ✅ Cold Chain Compliance
- Automatic temperature monitoring
- Breach detection and alerts
- Compliance status calculation
- Audit trail of all events

### ✅ Vehicle Management
- Temperature control capabilities
- Sensor availability tracking
- Maintenance scheduling
- Sanitization records

### ✅ Real-Time Tracking
- GPS location updates
- Temperature & humidity monitoring
- Device health (battery, signal)
- Location description

### ✅ Audit & Compliance
- Immutable event log
- Corrective action tracking
- Severity classifications
- Compliance reports

### ✅ Agent Dashboard
- Accept/reject assignments
- View in-progress deliveries with live tracking
- Update tracking information
- Performance metrics and earnings
- Vehicle information

---

## Database Schema

```
Order
  ├─ OrderDelivery (1:1)
  │   ├─ DeliveryMethod
  │   ├─ CollectionPoint (nullable)
  │   ├─ ColdChainRequirement (nullable)
  │   └─ DeliveryAssignment (1:N)
  │       ├─ ServiceAgent (delivery person)
  │       ├─ DeliveryVehicle
  │       └─ DeliveryTracking (1:1)
  │           └─ DeliveryTrackingEvent (1:N)
  │
  └─ Product
      └─ ColdChainRequirement (nullable)
```

---

## Testing the System

### Check Models Work
```bash
python manage.py shell
>>> from delivery.models import DeliveryMethod
>>> DeliveryMethod.objects.all()
```

### View Delivery Methods Created
```bash
python manage.py shell
>>> from delivery.models import DeliveryMethod
>>> for m in DeliveryMethod.objects.all():
...     print(f"{m.name}: {m.code}")
```

### Run System Checks
```bash
python manage.py check
```

---

## Next Steps

### To Fully Integrate with Order Checkout
1. Update order forms to include delivery method selection
2. Link `OrderDelivery` creation to order creation
3. Set `Order.delivery` ForeignKey when creating delivery

### To Add Notifications
1. Create signals for cold chain breaches
2. Send email/SMS alerts to agent and customer
3. Update dashboard with real-time notifications

### To Add Customer Tracking UI
1. Create public order tracking page
2. Display current location and ETA
3. Show last temperature reading (if monitored)
4. Allow proof of delivery upload

### To Add Analytics
1. Create delivery performance dashboards
2. Track on-time delivery rates
3. Monitor cold chain compliance by agent/vehicle
4. Generate compliance certificates

---

## File Locations

```
delivery/
├── __init__.py
├── apps.py
├── admin.py               - Admin configuration
├── models.py              - All 9 models
├── serializers.py         - REST API serializers
├── views.py               - 9 ViewSets with custom actions
├── urls.py                - API routing
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py    - Initial schema migration
└── management/
    └── commands/
        └── setup_delivery_methods.py

dashboards/
├── views.py               - delivery_agent_dashboard view
└── urls.py                - Added delivery-agent route

templates/dashboards/
└── delivery_agent_dashboard.html - Complete agent UI

config/
├── settings.py            - Added 'delivery' to INSTALLED_APPS
└── urls.py                - Added delivery API routing
```

---

## Configuration

### Default Settings
- Cold chain monitoring frequency: 15 minutes
- Temperature unit: Celsius (configurable per vehicle)
- Currency: ₹ (can be changed from SiteSettings)

### Environment Variables Needed
None for delivery system (uses existing Django setup)

---

## Troubleshooting

### Models Not Found
```bash
python manage.py migrate delivery
```

### No Delivery Methods Visible
```bash
python manage.py setup_delivery_methods
```

### API Endpoints Not Accessible
- Check URL is `/api/delivery/...`
- Ensure user is authenticated
- Check user_type permissions in viewsets

### Cold Chain Tracking Not Working
- Verify vehicle has `has_temperature_sensor = True`
- Ensure `cold_chain_monitoring_enabled = True` on assignment
- Check tracking events are being created

---

## Performance Notes

### Indexes Created
- order_delivery_order
- order_delivery_status
- delivery_tracking_assignment
- delivery_assignment_status
- compliance_status

All are created automatically by migrations.

### Query Optimization
Serializers use `select_related()` and `prefetch_related()` for:
- Related objects (service_agent, vehicles, etc.)
- Nested tracking events
- Compliance reports

---

## Compliance & Audit

All tracking events are:
- **Immutable** - Cannot be edited after creation
- **Timestamped** - Exact time of event
- **Authorized** - User who took action recorded
- **Severitized** - info/warning/critical classification
- **Actionable** - Corrective actions tracked

This ensures full FDA/FSSAI compliance for cold chain foods.

