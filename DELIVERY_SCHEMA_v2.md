# Delivery System - Database Schema & Design (with Cold Chain Tracking)

## Overview
The delivery system allows users to choose delivery methods with three options:
1. **Collection** - User collects order from a pre-defined location
2. **Home Delivery** - Delivery agent delivers to customer's address  
3. **Collections Point** - Order sent to a third-party location (shop, home, etc.)

**Key Feature:** Delivery agents track all aspects of transportation including cold chain storage, temperature maintenance, GPS tracking, and environmental conditions.

---

## Data Models

### 1. ColdChainRequirement
Specifies temperature and storage requirements for products/orders.

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
│• temperature_unit [choices]                  │
│  - 'C' (Celsius)                             │
│  - 'F' (Fahrenheit)                          │
│• storage_type [choices]                     │
│  - 'frozen'        (-18°C or below)          │
│  - 'refrigerated'  (2-8°C)                   │
│  - 'ambient'       (15-25°C)                 │
│  - 'dry'           (no moisture)             │
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

---

### 2. DeliveryVehicle
Tracks vehicle specifications and cold chain capabilities.

```
┌──────────────────────────────────────────────┐
│        DeliveryVehicle                       │
├──────────────────────────────────────────────┤
│• id (PK)                                     │
│• service_agent_id (FK → ServiceAgent)        │
│• vehicle_type [string]                       │
│  (e.g., "Car", "Motorcycle", "Truck")        │
│• registration_number [string] [unique]       │
│• vehicle_make_model [string]                 │
│• max_weight_capacity [decimal, kg]           │
│• max_volume_capacity [decimal, liters]       │
│• has_temperature_control [boolean]           │
│  (refrigerated/insulated compartment)        │
│• min_temp_capability [decimal, nullable]    │
│• max_temp_capability [decimal, nullable]    │
│• temperature_unit [choices]                  │
│  - 'C' (Celsius)                             │
│  - 'F' (Fahrenheit)                          │
│• has_gps_tracking [boolean]                  │
│  (device installed for location tracking)    │
│• has_temperature_sensor [boolean]            │
│  (IoT sensor for real-time temp monitoring)  │
│• has_humidity_sensor [boolean]               │
│  (sensor for humidity tracking)              │
│• maintenance_due_date [date, nullable]       │
│• last_sanitization_date [date, nullable]     │
│• last_temperature_calibration [date]         │
│• is_active [boolean]                         │
│• notes [text]                                │
│• created_at [datetime]                       │
│• updated_at [datetime]                       │
└──────────────────────────────────────────────┘
```

---

### 3. DeliveryMethod
Delivers options available to customers.

```
┌─────────────────────────────────┐
│      DeliveryMethod             │
├─────────────────────────────────┤
│• id (PK)                        │
│• name [string]                  │
│• code [unique string]           │
│• description [text]             │
│• method_type [choices]          │
│  - 'collection'                 │
│  - 'delivery' (home)            │
│  - 'collection_point' (3rd pty) │
│• is_active [boolean]            │
│• created_at [datetime]          │
│• updated_at [datetime]          │
└─────────────────────────────────┘
```

---

### 4. CollectionPoint
Locations where orders can be collected (shops, homes, etc.)

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
│• has_temperature_control [boolean]   │
│  (cold storage available at point)   │
│• is_active [boolean]                 │
│• notes [text]                        │
│• created_at [datetime]               │
│• updated_at [datetime]               │
└──────────────────────────────────────┘
```

---

### 5. OrderDelivery
Links orders to delivery details with cold chain tracking.

```
┌──────────────────────────────────────────────────────┐
│           OrderDelivery                              │
├──────────────────────────────────────────────────────┤
│• id (PK)                                             │
│• order_id (FK → Order) [unique]                      │
│• delivery_method_id (FK → DeliveryMethod)            │
│• delivery_status [choices]                           │
│  - 'pending'          (awaiting confirmation)        │
│  - 'confirmed'        (accepted by agent)            │
│  - 'in_transit'       (on the way)                   │
│  - 'delivered'        (completed delivery)           │
│  - 'collected'        (customer picked up)           │
│  - 'cancelled'                                       │
│• delivery_date [date, nullable]                      │
│• estimated_delivery_time [datetime, nullable]        │
│• actual_delivery_time [datetime, nullable]           │
│• delivery_address [text]                             │
│• delivery_city [string]                              │
│• delivery_state [string]                             │
│• delivery_zip_code [string]                          │
│• collection_point_id (FK → CollectionPoint)          │
│  [nullable - only for collection_point method]       │
│• cold_chain_requirement_id (FK → ColdChainReq)       │
│  [nullable - if order has cold chain needs]          │
│• delivery_notes [text]                               │
│• special_instructions [text]                         │
│• signature_required [boolean]                        │
│• proof_of_delivery [image, nullable]                 │
│• cold_chain_compliance [choices]                     │
│  - 'compliant'   (maintained within spec)            │
│  - 'warning'     (minor deviation, recoverable)      │
│  - 'breach'      (out of spec, data compromised)     │
│  - 'unchecked'   (not monitored)                     │
│• cold_chain_compliance_notes [text]                  │
│• total_hours_in_transit [integer, nullable]          │
│• created_at [datetime]                               │
│• updated_at [datetime]                               │
└──────────────────────────────────────────────────────┘
```

---

### 6. DeliveryTracking
Real-time tracking of vehicle location and environmental conditions.

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
│  (°C or °F depending on vehicle setting)     │
│• temperature_unit [choices]                  │
│  - 'C' (Celsius)                             │
│  - 'F' (Fahrenheit)                          │
│• temperature_deviation [decimal, nullable]   │
│  (actual - required, null if compliant)      │
│• ambient_temperature [decimal, nullable]     │
│  (outside temperature)                       │
│• humidity_percentage [decimal, nullable]     │
│  (inside vehicle)                            │
│• vehicle_temperature_status [choices]        │
│  - 'optimal'  (within spec)                  │
│  - 'warning'  (approaching limit)            │
│  - 'critical' (out of spec, breach)          │
│• gps_accuracy [decimal, nullable]            │
│  (accuracy in meters)                        │
│• battery_level [decimal, nullable]           │
│  (for GPS/sensor device %)                   │
│• signal_strength [integer, nullable]         │
│  (cellular/network signal strength)          │
│• tracked_at [datetime]                       │
│• created_at [datetime]                       │
│• updated_at [datetime]                       │
└──────────────────────────────────────────────┘
```

---

### 7. DeliveryTrackingEvent
Historical audit log of all delivery tracking events.

```
┌──────────────────────────────────────────────┐
│     DeliveryTrackingEvent                    │
├──────────────────────────────────────────────┤
│• id (PK)                                     │
│• delivery_tracking_id (FK)                   │
│• event_type [choices]                        │
│  - 'temperature_reading' (periodic)          │
│  - 'location_update' (GPS update)            │
│  - 'deviation_detected' (out of spec)        │
│  - 'system_breach' (temp exceed')            │
│  - 'manual_entry' (agent recorded)           │
│  - 'status_change' (delivery progress)       │
│  - 'sensor_failure' (device malfunction)     │
│  - 'door_opened' (fridge door opened)        │
│• event_description [text]                    │
│• temperature [decimal, nullable]             │
│• latitude [decimal, nullable]                │
│• longitude [decimal, nullable]               │
│• event_severity [choices]                    │
│  - 'info'     (informational)                │
│  - 'warning'  (minor concern)                │
│  - 'critical' (serious issue)                │
│• requires_action [boolean]                   │
│  (flag for compliance issue)                 │
│• action_taken [text, nullable]               │
│• action_taken_by_id (FK → CustomUser)        │
│  [nullable - who corrected it]               │
│• action_taken_at [datetime, nullable]        │
│• created_at [datetime]                       │
└──────────────────────────────────────────────┘
```

---

### 8. DeliveryAssignment
Assigns delivery agents and vehicles to orders.

```
┌───────────────────────────────────────────────────┐
│      DeliveryAssignment                           │
├───────────────────────────────────────────────────┤
│• id (PK)                                          │
│• order_delivery_id (FK → OrderDelivery)           │
│• delivery_agent_id (FK → ServiceAgent)            │
│• assigned_vehicle_id (FK → DeliveryVehicle)       │
│• delivery_tracking_id (FK → DeliveryTracking)     │
│• assignment_status [choices]                      │
│  - 'assigned'      (pending agent acceptance)     │
│  - 'accepted'      (agent confirmed)              │
│  - 'rejected'      (agent declined)               │
│  - 'in_progress'   (currently delivering)         │
│  - 'completed'     (delivered/collected)          │
│  - 'failed'        (couldn't complete)            │
│• vehicle_suitability_check [choices]              │
│  - 'suitable'      (meets cold chain specs)       │
│  - 'marginal'      (barely meets specs)           │
│  - 'unsuitable'    (cannot meet requirements)     │
│• vehicle_suitability_notes [text]                 │
│• assigned_at [datetime]                           │
│• accepted_at [datetime, nullable]                 │
│• started_at [datetime, nullable]                  │
│• completed_at [datetime, nullable]                │
│• delivery_fee [decimal]                           │
│• cold_chain_monitoring_enabled [boolean]          │
│• monitoring_frequency_minutes [integer]           │
│  (how often to record data - default 15 min)      │
│• pickup_time [datetime, nullable]                 │
│  (when agent picked up order from facility)       │
│• last_sensor_reading_time [datetime, nullable]    │
│• compliance_check_passed [boolean, nullable]      │
│• notes [text]                                     │
│• created_at [datetime]                            │
│• updated_at [datetime]                            │
└───────────────────────────────────────────────────┘
```

---

## Relationships Diagram

```
┌──────────────────────────────────────┐
│      CustomUser (Subscriber)         │
└────┬─────────────────────────────────┘
     │
     └─→ Order (1:N)
         │
         ├─→ OrderDelivery (1:1)
         │   │
         │   ├─→ DeliveryMethod
         │   │   (collection | delivery | collection_point)
         │   │
         │   ├─→ ColdChainRequirement (nullable)
         │   │
         │   ├─→ CollectionPoint (nullable)
         │   │
         │   └─→ DeliveryAssignment (1:N)
         │       │
         │       ├─→ ServiceAgent (delivery person)
         │       │
         │       ├─→ DeliveryVehicle
         │       │   (specs, temp capability, sensors)
         │       │
         │       └─→ DeliveryTracking (real-time)
         │           │
         │           └─→ DeliveryTrackingEvent (N:N audit log)
         │
         └─→ Product (via OrderItem)
             │
             └─→ ColdChainRequirement


┌──────────────────────────────────┐
│  CustomUser (Delivery Agent)      │
└────┬─────────────────────────────┘
     │
     └─→ ServiceAgent
         │
         └─→ DeliveryVehicle (multiple)
             │
             └─→ DeliveryAssignment (N)
                 │
                 └─→ OrderDelivery
```

---

## Cold Chain Tracking Workflow

### Temperature Monitoring During Delivery

```
1. Order Created
   → ColdChainRequirement set (if frozen/refrigerated product)
   → Min/max temp and max delivery time defined

2. Agent Assigned
   → DeliveryAssignment created
   → System checks vehicle_suitability:
     - Vehicle temp capability >= order requirement?
     - Vehicle has sensors? Enable monitoring
   → monitoring_frequency_minutes set (e.g., every 15min)

3. Pickup
   → Agent picks up order
   → pickup_time recorded
   → DeliveryTracking created

4. During Transit (Every 15 minutes or real-time)
   → Sensor reads temperature/humidity
   → DeliveryTracking updated
   → DeliveryTrackingEvent logged
   → If temperature out of spec:
     - vehicle_temperature_status = 'critical'
     - DeliveryTrackingEvent created with severity='critical'
     - Alert sent to system/manager

5. Delivery Complete
   → actual_delivery_time set
   → total_hours_in_transit calculated
   → System calculates cold_chain_compliance:
     - If any critical events: 'breach'
     - If warnings but recovered: 'warning'
     - If always in spec: 'compliant'
     - If not monitored: 'unchecked'
   → OrderDelivery.cold_chain_compliance updated
   → Compliance report generated
```

### Manual Temperature Check (No Sensors)

```
1. If vehicle has no temperature sensor:
   → DeliveryTracking can be filled manually by agent
   → Agent records temp/location periodically via app

2. Each manual entry creates:
   → DeliveryTrackingEvent with event_type='manual_entry'
   → Later reviewed for compliance

3. Automatic alerts still possible:
   → Agent reports issue immediately
   → system_breach event created
   → Corrective action required
```

---

## Database Indexes (Performance)

```sql
CREATE INDEX idx_cold_chain_req_product ON delivery_coldchainrequirement(product_id);
CREATE INDEX idx_delivery_vehicle_agent ON delivery_deliveryvehicle(service_agent_id);
CREATE INDEX idx_delivery_vehicle_active ON delivery_deliveryvehicle(is_active);

CREATE INDEX idx_order_delivery_order ON delivery_orderdelivery(order_id);
CREATE INDEX idx_order_delivery_method ON delivery_orderdelivery(delivery_method_id);
CREATE INDEX idx_order_delivery_status ON delivery_orderdelivery(delivery_status);
CREATE INDEX idx_order_delivery_compliance ON delivery_orderdelivery(cold_chain_compliance);
CREATE INDEX idx_order_delivery_collection_point ON delivery_orderdelivery(collection_point_id);

CREATE INDEX idx_delivery_tracking_assignment ON delivery_deliverytracking(delivery_assignment_id);
CREATE INDEX idx_delivery_tracking_status ON delivery_deliverytracking(vehicle_temperature_status);
CREATE INDEX idx_delivery_tracking_time ON delivery_deliverytracking(tracked_at);

CREATE INDEX idx_tracking_event_tracking ON delivery_deliverytrackingevet(delivery_tracking_id);
CREATE INDEX idx_tracking_event_type ON delivery_deliverytrackingevet(event_type);
CREATE INDEX idx_tracking_event_severity ON delivery_deliverytrackingevet(event_severity);

CREATE INDEX idx_delivery_assignment_order ON delivery_deliveryassignment(order_delivery_id);
CREATE INDEX idx_delivery_assignment_agent ON delivery_deliveryassignment(delivery_agent_id);
CREATE INDEX idx_delivery_assignment_vehicle ON delivery_deliveryassignment(assigned_vehicle_id);
CREATE INDEX idx_delivery_assignment_status ON delivery_deliveryassignment(assignment_status);
CREATE INDEX idx_delivery_assignment_compliance ON delivery_deliveryassignment(assignment_status, compliance_check_passed);
```

---

## Integration with Existing Models

### Order Model
Add field:
```python
delivery = models.OneToOneField(
    'delivery.OrderDelivery',
    on_delete=models.SET_NULL,
    null=True,
    related_name='order'
)
```

### ServiceAgent Model (Users)
Already has `vehicle_type`, but should have:
```python
vehicles = models.OneToManyField(  # multiple vehicles possible
    'delivery.DeliveryVehicle',
    related_name='service_agent'
)
```

---

## Key Design Decisions

1. **Separate Tracking Models**: DeliveryTracking for real-time + DeliveryTrackingEvent for audit log
2. **Cold Chain at Multiple Levels**: Product-level + Order-level requirements
3. **Flexible Vehicle Specs**: Can track any vehicle with any temp range/sensors
4. **Manual Override**: Data can be entered manually if sensors unavailable
5. **Compliance Status**: Calculated at delivery completion, not real-time
6. **Sensor Integration Ready**: Fields for GPS accuracy, battery, signal for IoT integration
7. **Audit Trail**: Every event logged immutably for compliance/legal requirements
