# Delivery System - Database Schema & Design

## Overview
The delivery system allows users to choose delivery methods with three options:
1. **Collection** - User collects order from a pre-defined location
2. **Home Delivery** - Delivery agent delivers to customer's address
3. **Collections Point** - Order sent to a third-party location (shop, home, etc.)

---

## New Models

### 1. DeliveryTracking
Real-time tracking of order transportation with environmental conditions (cold chain, temperature, location).

```
┌──────────────────────────────────────────────┐
│       DeliveryTracking                       │
├──────────────────────────────────────────────┤
│• id (PK)                                     │
│• delivery_assignment_id (FK)                 │
│• current_latitude [decimal, nullable]        │
│• current_longitude [decimal, nullable]       │
│• current_location_description [string]       │
│• current_temperature [decimal, nullable]     │
│• temperature_unit [choices]                  │
│  - 'C' (Celsius)                             │
│  - 'F' (Fahrenheit)                          │
│• temperature_deviation [decimal, nullable]   │
│  (actual - required, null if compliant)      │
│• ambient_temperature [decimal, nullable]     │
│• humidity_percentage [decimal, nullable]     │
│• vehicle_temperature_status [choices]        │
│  - 'optimal' (within range)                  │
│  - 'warning' (approaching limit)             │
│  - 'critical' (out of range)                 │
│• gps_accuracy [decimal, nullable]            │
│  (accuracy in meters)                        │
│• tracked_at [datetime]                       │
│• updated_at [datetime]                       │
└──────────────────────────────────────────────┘
```

**Fields:**
- Real-time data from IoT sensors or manual entry
- `temperature_deviation`: Alerts if temp goes out of spec
- `vehicle_temperature_status`: Used for alerts and compliance
- `tracked_at`: Timestamp of each tracking event

---

### 2. DeliveryTrackingEvent
Historical log of all tracking events for audit trail and compliance.

```
┌─────────────────────────────────────────────┐
│    DeliveryTrackingEvent                    │
├─────────────────────────────────────────────┤
│• id (PK)                                    │
│• delivery_tracking_id (FK)                  │
│• event_type [choices]                       │
│  - 'temperature_reading'                    │
│  - 'location_update'                        │
│  - 'deviation_detected'                     │
│  - 'system_breach'                          │
│  - 'manual_entry'                           │
│  - 'status_change'                          │
│  - 'sensor_failure'                         │
│• event_description [text]                   │
│• temperature [decimal, nullable]            │
│• latitude [decimal, nullable]               │
│• longitude [decimal, nullable]              │
│• event_severity [choices]                   │
│  - 'info'                                   │
│  - 'warning'                                │
│  - 'critical'                               │
│• requires_action [boolean]                  │
│• action_taken [text, nullable]              │
│• action_taken_by_id (FK → CustomUser)       │
│• created_at [datetime]                      │
└─────────────────────────────────────────────┘
```

**Fields:**
- Complete audit trail of delivery conditions
- `requires_action`: Flag for compliance or quality issues
- `action_taken`: Record of corrective actions
- Immutable historical record

---

### 3. ColdChainRequirement
Specifies temperature and storage requirements for orders.

```
┌──────────────────────────────────────────────┐
│      ColdChainRequirement                    │
├──────────────────────────────────────────────┤
│• id (PK)                                     │
│• product_id (FK → Product) [nullable]        │
│• name [string]                               │
│  (e.g., "Frozen", "Refrigerated", "Ambient")│
│• min_temperature [decimal]                   │
│• max_temperature [decimal]                   │
│• temperature_unit [choices] - 'C' or 'F'    │
│• storage_type [choices]                     │
│  - 'frozen'                                  │
│  - 'refrigerated'                            │
│  - 'ambient'                                 │
│  - 'dry'                                     │
│• max_humidity_percentage [decimal]           │
│• requires_insulation [boolean]               │
│• requires_ice_packs [boolean]                │
│• max_delivery_hours [integer]                │
│  (maximum hours from pickup to delivery)     │
│• notes [text]                                │
│• created_at [datetime]                       │
│• updated_at [datetime]                       │
└──────────────────────────────────────────────┘
```

**Fields:**
- Can be product-level or order-level
- `max_delivery_hours`: Enforce time limits for perishables
- Multiple requirements per order possible
- Defines delivery vehicle specifications needed

---

### 4. DeliveryMethod
Manages the different delivery options available to customers.

```
┌─────────────────────────────────┐
│      DeliveryMethod             │
├─────────────────────────────────┤
│• id (PK)                        │
│• name [string]                  │
│• code [unique string]           │
│• description [text]             │
│• method_type [choices]          │
│  - 'collection' (collect)       │
│  - 'delivery' (home delivery)   │
│  - 'collection_point' (3rd party)│
│• is_active [boolean]            │
│• created_at [datetime]          │
│• updated_at [datetime]          │
└─────────────────────────────────┘
```

**Fields:**
- `name`: e.g., "Standard Delivery", "Pick Up", "Shop Collection"
- `code`: e.g., "STD_DELIVERY", "PICKUP", "SHOP_COLLECT"
- `method_type`: Determines which delivery model applies
- `is_active`: Can be disabled without deleting historical data

---

### 7. DeliveryAssignment (REVISED)
Assigns delivery agents and vehicles to orders with cold chain tracking.

```
┌────────────────────────────────────────────────────┐
│      DeliveryAssignment                            │
├────────────────────────────────────────────────────┤
│• id (PK)                                           │
│• order_delivery_id (FK → OrderDelivery)            │
│• delivery_agent_id (FK → ServiceAgent)             │
│• assigned_vehicle_id (FK → DeliveryVehicle)        │
│• delivery_tracking_id (FK → DeliveryTracking)      │
│• assignment_status [choices]                       │
│  - 'assigned'      (pending acceptance)            │
│  - 'accepted'      (agent confirmed)               │
│  - 'rejected'      (agent declined)                │
│  - 'in_progress'   (on the way)                    │
│  - 'completed'     (delivered/collected)           │
│• vehicle_suitability_check [choices]               │
│  - 'suitable'      (vehicle meets requirements)    │
│  - 'marginal'      (barely meets specs)            │
│  - 'unsuitable'    (cannot meet requirements)      │
│• vehicle_suitability_notes [text]                  │
│• assigned_at [datetime]                            │
│• accepted_at [datetime, nullable]                  │
│• started_at [datetime, nullable]                   │
│• completed_at [datetime, nullable]                 │
│• delivery_fee [decimal]                            │
│• cold_chain_monitoring_enabled [boolean]           │
│• monitoring_frequency_minutes [integer]            │
│  (how often to record temperature, default 15)     │
│• pickup_time [datetime, nullable]                  │
│• notes [text]                                      │
│• created_at [datetime]                             │
│• updated_at [datetime]                             │
└────────────────────────────────────────────────────┘
```

**Fields:**
- `assigned_vehicle_id`: Links to vehicle with specific capabilities
- `vehicle_suitability_check`: Validates vehicle meets cold chain needs
- `delivery_tracking_id`: Real-time data from vehicle sensors
- `cold_chain_monitoring_enabled`: Toggles temperature tracking
- `monitoring_frequency_minutes`: Controls data collection frequency

---

### 6. CollectionPoint (UNCHANGED)
Locations where orders can be collected (shops, homes, community centers, etc.)

```
┌──────────────────────────────────────┐
│       CollectionPoint                │
├──────────────────────────────────────┤
│• id (PK)                             │
│• name [string]                       │
│• owner_user_id (FK → CustomUser)     │
│• location_type [choices]             │
│  - 'shop'                            │
│  - 'home'                            │
│  - 'community_center'                │
│  - 'other'                           │
│• address [text]                      │
│• city [string]                       │
│• state [string]                      │
│• zip_code [string]                   │
│• latitude [decimal, nullable]        │
│• longitude [decimal, nullable]       │
│• phone [string]                      │
│• email [email, nullable]             │
│• operating_hours_start [time]        │
│• operating_hours_end [time]          │
│• max_storage_capacity [integer]      │
│• current_orders_count [integer]      │
│• is_active [boolean]                 │
│• notes [text]                        │
│• created_at [datetime]               │
│• updated_at [datetime]               │
└──────────────────────────────────────┘
```

**Fields:**
- `owner_user_id`: User who manages this collection point (shop owner, community center manager, etc.)
- `location_type`: Type of location for filtering/categorization
- `latitude/longitude`: For map integration and distance calculation
- `operating_hours_start/end`: When collection is available
- `max_storage_capacity`: How many orders can be stored
- `current_orders_count`: Track current orders at this point
- `is_active`: Can disable collection point temporarily

---

### 5. DeliveryVehicle
Tracks vehicle specifications and capabilities for delivery agents.

```
┌──────────────────────────────────────────┐
│        DeliveryVehicle                   │
├──────────────────────────────────────────┤
│• id (PK)                                 │
│• service_agent_id (FK → ServiceAgent)    │
│• vehicle_type [string]                   │
│  (e.g., "Car", "Motorcycle", "Truck")    │
│• registration_number [string]            │
│• vehicle_make_model [string]             │
│• max_weight_capacity [decimal]           │
│• max_volume_capacity [decimal]           │
│  (in liters or cubic meters)             │
│• has_temperature_control [boolean]       │
│• min_temp_capability [decimal, nullable] │
│• max_temp_capability [decimal, nullable] │
│• temperature_unit [choices]              │
│  - 'C' (Celsius)                         │
│  - 'F' (Fahrenheit)                      │
│• has_gps_tracking [boolean]              │
│• has_temperature_sensor [boolean]        │
│• has_humidity_sensor [boolean]           │
│• maintenance_due_date [date, nullable]   │
│• last_sanitization_date [date, nullable] │
│• is_active [boolean]                     │
│• notes [text]                            │
│• created_at [datetime]                   │
│• updated_at [datetime]                   │
└──────────────────────────────────────────┘
```

**Fields:**
- Defines vehicle capabilities for cold chain compliance
- `has_gps_tracking`: Enables real-time location tracking
- `has_temperature_sensor`: Enables automatic temperature monitoring
- Sanitization/maintenance tracking for food safety

---

### 6. OrderDelivery (REVISED)
Links orders to delivery details and tracks delivery progress with cold chain monitoring.

```
┌──────────────────────────────────────────────────┐
│           OrderDelivery                          │
├──────────────────────────────────────────────────┤
│• id (PK)                                         │
│• order_id (FK → Order) [unique]                  │
│• delivery_method_id (FK → DeliveryMethod)        │
│• delivery_status [choices]                       │
│  - 'pending'          (waiting)                  │
│  - 'confirmed'        (accepted)                 │
│  - 'in_transit'       (on the way)               │
│  - 'delivered'        (completed)                │
│  - 'collected'        (by customer)              │
│  - 'cancelled'                                   │
│• delivery_date [date, nullable]                  │
│• estimated_delivery_time [datetime, nullable]    │
│• actual_delivery_time [datetime, nullable]       │
│• delivery_address [text]                         │
│• delivery_city [string]                          │
│• delivery_state [string]                         │
│• delivery_zip_code [string]                      │
│• collection_point_id (FK → CollectionPoint)      │
│  [nullable - only for collection_point]          │
│• cold_chain_requirement_id (FK to requirement)   │
│  [nullable - if order has cold chain needs]      │
│• delivery_notes [text]                           │
│• special_instructions [text]                     │
│• signature_required [boolean]                    │
│• proof_of_delivery [image, nullable]             │
│• cold_chain_compliance [choices]                 │
│  - 'compliant'   (maintained within spec)        │
│  - 'warning'     (minor deviation)               │
│  - 'breach'      (out of spec)                   │
│  - 'unchecked'   (not monitored)                 │
│• cold_chain_compliance_notes [text]              │
│• created_at [datetime]                           │
│• updated_at [datetime]                           │
└──────────────────────────────────────────────────┘
```

**Fields:**
- `delivery_method_id`: Links to the delivery method chosen
- `delivery_status`: Tracks progress through delivery pipeline
- `delivery_address`: For home deliveries (customer's address)
- `collection_point_id`: For collection point deliveries
- `estimated_delivery_time`: ETA for customer
- `proof_of_delivery`: Photo/signature confirmation
- `special_instructions`: Instructions for delivery agent

---

### 4. DeliveryAssignment
Assigns delivery agents to orders (for home delivery and collection point delivery).

```
┌─────────────────────────────────────────────┐
│      DeliveryAssignment                     │
├─────────────────────────────────────────────┤
│• id (PK)                                    │
│• order_delivery_id (FK → OrderDelivery)     │
│• delivery_agent_id (FK → ServiceAgent)      │
│• assignment_status [choices]                │
│  - 'assigned'      (pending acceptance)     │
│  - 'accepted'      (agent confirmed)        │
│  - 'rejected'      (agent declined)         │
│  - 'in_progress'   (on the way)             │
│  - 'completed'     (delivered/collected)    │
│• assigned_at [datetime]                     │
│• accepted_at [datetime, nullable]           │
│• started_at [datetime, nullable]            │
│• completed_at [datetime, nullable]          │
│• delivery_fee [decimal]                     │
│• notes [text]                               │
│• created_at [datetime]                      │
│• updated_at [datetime]                      │
└─────────────────────────────────────────────┘
```

**Fields:**
- `delivery_agent_id`: References ServiceAgent (delivery person)
- `assignment_status`: Tracks assignment lifecycle
- `delivery_fee`: Cost for this delivery (may differ per agent)
- Allows tracking which agent delivered

---

## Modified Models

### Order Model Updates
Add field to reference delivery information:

```python
class Order(models.Model):
    # ...existing fields...
    
    # Add delivery tracking
    delivery = models.OneToOneField(
        'OrderDelivery', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='order'
    )
```

---

## Relationships Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     CustomUser (Subscriber)                    │
└──┬─────────────────────────────────────────────────────────────┘
   │
   └─────→ Order (many)
            │
            ├─→ OrderDelivery (1:1) 
            │   │
            │   ├─→ DeliveryMethod
            │   │   (collection | delivery | collection_point)
            │   │
            │   ├─→ CollectionPoint (nullable, for collection_point)
            │   │
            │   └─→ DeliveryAssignment (many, for delivery & collection_point)
            │       │
            │       └─→ ServiceAgent (delivery person)


┌────────────────────────────────────────────────────────────────┐
│              CustomUser (Collection Point Owner)               │
└──┬─────────────────────────────────────────────────────────────┘
   │
   └─────→ CollectionPoint (many)
            │
            └─→ OrderDelivery (many, incoming orders)


┌────────────────────────────────────────────────────────────────┐
│           CustomUser (Delivery Person/Service Agent)           │
└──┬─────────────────────────────────────────────────────────────┘
   │
   └─────→ ServiceAgent
            │
            └─→ DeliveryAssignment (many)
                │
                └─→ OrderDelivery
```

---

## Delivery Workflow Examples

### Example 1: Home Delivery
```
1. Customer chooses "Home Delivery" method
   → DeliveryMethod.method_type = 'delivery'
   → OrderDelivery created with delivery_address = customer's address

2. System assigns delivery agent
   → DeliveryAssignment created with delivery_agent_id

3. Agent accepts assignment
   → DeliveryAssignment.assignment_status = 'accepted'
   → OrderDelivery.delivery_status = 'confirmed'

4. Agent starts delivery
   → DeliveryAssignment.assignment_status = 'in_progress'
   → OrderDelivery.delivery_status = 'in_transit'

5. Order delivered
   → DeliveryAssignment.assignment_status = 'completed'
   → OrderDelivery.delivery_status = 'delivered'
   → OrderDelivery.actual_delivery_time set
   → OrderDelivery.proof_of_delivery may be captured
```

### Example 2: Collection Point Delivery
```
1. Customer chooses "Shop Collection" method
   → DeliveryMethod.method_type = 'collection_point'
   → CollectionPoint selected (e.g., local shop)
   → OrderDelivery created with collection_point_id

2. System assigns delivery agent to transport to point
   → DeliveryAssignment created

3. Agent delivers to collection point
   → DeliveryAssignment.assignment_status = 'completed'
   → OrderDelivery.delivery_status = 'at_collection_point'

4. Customer collects from shop
   → OrderDelivery.delivery_status = 'collected'
   → OrderDelivery.actual_delivery_time set
```

### Example 3: Customer Collection
```
1. Customer chooses "Pick Up" method
   → DeliveryMethod.method_type = 'collection'
   → OrderDelivery created (no delivery_address needed)
   → Collection location/time set

2. No delivery assignment needed

3. Customer picks up
   → OrderDelivery.delivery_status = 'collected'
   → OrderDelivery.actual_delivery_time set
```

---

## Database Indexes (For Performance)

```sql
CREATE INDEX idx_order_delivery_order ON delivery_orderdelivery(order_id);
CREATE INDEX idx_order_delivery_method ON delivery_orderdelivery(delivery_method_id);
CREATE INDEX idx_order_delivery_status ON delivery_orderdelivery(delivery_status);
CREATE INDEX idx_order_delivery_collection_point ON delivery_orderdelivery(collection_point_id);

CREATE INDEX idx_delivery_assignment_order ON delivery_deliveryassignment(order_delivery_id);
CREATE INDEX idx_delivery_assignment_agent ON delivery_deliveryassignment(delivery_agent_id);
CREATE INDEX idx_delivery_assignment_status ON delivery_deliveryassignment(assignment_status);

CREATE INDEX idx_collection_point_owner ON delivery_collectionpoint(owner_user_id);
CREATE INDEX idx_collection_point_active ON delivery_collectionpoint(is_active);
CREATE INDEX idx_collection_point_location ON delivery_collectionpoint(city, location_type);
```

---

## Integration Points

### With Order Model
- `Order.delivery` links to `OrderDelivery` (one-to-one)
- `Order.status` includes delivery states like 'in_transit', 'delivered'

### With ServiceAgent
- Delivery agents (ServiceAgent with service_type='delivery') get assigned via DeliveryAssignment
- Can filter available agents by vehicle type, capacity, location

### With Billing
- Delivery fees from `DeliveryAssignment.delivery_fee` are added to order total
- Tracked in Order.service_fee as part of `OrderServiceAgent` OR in a separate delivery fee

---

## Migration Strategy

1. Create `delivery` app (if not exists)
2. Create models in order:
   - `DeliveryMethod`
   - `CollectionPoint`
   - `OrderDelivery`
   - `DeliveryAssignment`
3. Update Order model to add `delivery` ForeignKey
4. Create initial DeliveryMethod records (Collection, Delivery, Collection Point)
5. Create management command to populate existing orders with default delivery method

---

## Key Design Decisions

1. **OrderDelivery as Separate Model**: Keeps Order model clean, allows tracking delivery independently
2. **DeliveryMethod**: Flexible for future expansion (e.g., drone delivery, locker pickup)
3. **Collection Points**: Generic owner_user_id allows shops, homes, or any location to be a collection point
4. **Separate DeliveryAssignment**: Allows multiple agents per order (e.g., warehouse + final delivery), audit trail
5. **Detailed Status Fields**: enabled accurate tracking and notifications
6. **No Separate Delivery Fee Model**: Fees stored in DeliveryAssignment, integrated with Order.service_fee

