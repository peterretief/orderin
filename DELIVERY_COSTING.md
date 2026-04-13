# Delivery Costing System Documentation

## Overview

The delivery costing system calculates delivery fees based on multiple factors:
- **Base price** (determined by distance and delivery method)
- **Weight surcharges** (for heavy items)
- **Temperature control surcharges** (for cold chain items)
- **Additional surcharges** (signature required, rush delivery, etc.)
- **Discounts** (percentage or fixed amount)
- **Taxes**

## Database Models

### 1. DeliveryPricingTier
Base pricing structure for each delivery method with distance-based tiers.

**Fields:**
- `delivery_method` - ForeignKey to DeliveryMethod
- `min_distance` - Minimum distance for this tier (km/miles)
- `max_distance` - Maximum distance for this tier
- `base_price` - Fixed price for this distance range
- `price_per_unit_distance` - Additional cost per km/mile
- `price_per_kg` - Additional cost per kilogram (optional)

**Example Pricing (Home Delivery):**
```
0-5km:        R50 base + R5/km
5-15km:       R75 base + R3/km
15-30km:      R120 base + R2/km
30+km:        R180 base + R1.50/km
```

### 2. WeightBasedPricing
Weight-based surcharges for heavy items.

**Fields:**
- `min_weight_kg` - Minimum weight for this surcharge
- `max_weight_kg` - Maximum weight for this surcharge
- `surcharge_percentage` - Percentage surcharge on base price
- `surcharge_fixed` - Fixed amount surcharge
- `applies_to_all_methods` - Whether to apply to all delivery methods
- `delivery_methods` - Specific delivery methods (if not all)

**Example Surcharges:**
```
0-5kg:        0% + R0 (standard)
5-15kg:       15% + R20 (heavy items)
15-30kg:      25% + R50 (very heavy)
30+kg:        35% + R100 (oversized)
```

### 3. TempControlPricing
Temperature control surcharges for cold chain items.

**Fields:**
- `storage_type` - Type of temp control needed (frozen, refrigerated, ambient, dry)
- `surcharge_percentage` - Percentage surcharge
- `surcharge_fixed` - Fixed amount surcharge
- `requires_vehicle_capability` - Must be delivered in temp-controlled vehicle

**Example Surcharges:**
```
Frozen:       30% + R75
Refrigerated: 20% + R50
Ambient:      0% + R0 (no surcharge)
Dry:          10% + R25
```

### 4. DeliveryCost
Stores the calculated delivery cost breakdown for a specific order.

**Fields:**
- `order_delivery` - OneToOneField to OrderDelivery
- `base_price` - Base price from pricing tier
- `distance_km` - Delivery distance
- `distance_charge` - Additional charge for distance
- `actual_weight_kg` - Actual weight in kilograms
- `weight_surcharge` - Weight-based surcharge
- `temp_control_surcharge` - Temperature control surcharge
- `signature_required_surcharge` - Signature surcharge
- `rush_delivery_surcharge` - Rush delivery surcharge
- `other_surcharges` - Any other charges
- `discount_percentage` - Percentage discount
- `discount_amount` - Fixed discount
- `tax_percentage` - Tax rate
- `tax_amount` - Calculated tax
- `subtotal` - Total before tax
- `total_cost` - Final total with tax

## Usage

### 1. Accessing the Cost Calculation Service

```python
from delivery.costing import DeliveryCostCalculator, calculate_delivery_cost

# Method 1: Using convenience function
cost = calculate_delivery_cost(
    order_delivery=order_delivery,
    distance_km=12.5,
    actual_weight_kg=8.2,
    tax_percentage=15
)
print(f"Total cost: R{cost.total_cost}")
```

### 2. Manual Calculation with Details

```python
# Method 2: Using the calculator class
calculator = DeliveryCostCalculator(
    order_delivery=order_delivery,
    distance_km=12.5,
    actual_weight_kg=8.2
)

# Add optional surcharges
calculator.add_surcharges(
    signature_required=True,
    rush_delivery=False,
    other_amount=Decimal('25')
)

# Apply discounts
calculator.apply_discount(discount_percentage=5)

# Apply tax
calculator.apply_tax(tax_percentage=15)

# Calculate
result = calculator.calculate()
print(result)
# {
#     'subtotal': Decimal('123.45'),
#     'total_cost': Decimal('141.97'),
#     'breakdown': {...}
# }

# Save to database
cost = calculator.save_cost(tax_percentage=15)
```

### 3. Cost Breakdown Example

For an order with:
- Delivery method: Home Delivery
- Distance: 12.5km
- Weight: 8.2kg
- Cold chain: Refrigerated
- Signature: Not required
- Tax: 15%

**Calculation:**
```
Base price (5-15km tier):     R75
Distance charge (7.5km × R3): R22.50
Weight surcharge (8.2kg):     R20 + 15% = R32.50  
Temp control (refrigerated):  R50 + 20% = R60
Subtotal:                      R190.00
Discount:                      R0
Tax (15%):                     R28.50
TOTAL:                         R218.50
```

## Admin Interface

Access delivery pricing configuration through Django admin:
- `/admin/delivery/deliverypricingstier/` - Manage distance-based pricing
- `/admin/delivery/weightbasedpricing/` - Manage weight surcharges
- `/admin/delivery/tempcontrolpricing/` - Manage temperature surcharges
- `/admin/delivery/deliverycost/` - View calculated costs

## API Endpoints

New REST API endpoints for delivery pricing:

```
GET    /api/delivery/pricing-tiers/              - List all pricing tiers
POST   /api/delivery/pricing-tiers/              - Create pricing tier
GET    /api/delivery/pricing-tiers/{id}/         - Get specific tier

GET    /api/delivery/planning-settings/my_settings/ - Get cost history
```

## Features

✅ **Distance-based pricing** - Different rates for different distance ranges
✅ **Weight surcharges** - Extra charges for heavy items
✅ **Temperature control** - Premium pricing for cold chain requirements
✅ **Flexible surcharges** - Support for signature, rush delivery, etc.
✅ **Discounts** - Both percentage and fixed amount discounts
✅ **Tax calculation** - Automatic tax computation
✅ **Cost breakdown** - Detailed breakdown of all charges
✅ **Per-kg pricing** - Optional per-kilogram charges

## Configuration Steps

1. **Set up pricing tiers** in Django admin
2. **Define weight surcharges** for different weight ranges
3. **Configure temperature surcharges** for each storage type
4. **Use costing service** during order checkout to calculate final cost
5. **Display cost** to customer before confirming delivery

## Example: Adding Custom Pricing

```python
from delivery.models import DeliveryPricingTier, DeliveryMethod
from decimal import Decimal

# Get delivery method
home_delivery = DeliveryMethod.objects.get(name='home_delivery')

# Create new pricing tier
tier = DeliveryPricingTier.objects.create(
    delivery_method=home_delivery,
    min_distance=Decimal('50'),
    max_distance=Decimal('100'),
    base_price=Decimal('250'),
    price_per_unit_distance=Decimal('1'),
    distance_unit='km',
    is_active=True,
    notes='Regional delivery tier'
)
```

## Integration with Order Checkout

When a subscriber selects a delivery method:

1. Calculate delivery distance (if home delivery)
2. Get order weight from items
3. Check for cold chain requirements
4. Use `DeliveryCostCalculator` to compute cost
5. Show cost breakdown to customer
6. Add cost to order total
7. Save cost record for tracking

## Next Steps

- Integrate with Google Maps API for distance calculation
- Implement route optimization to suggest cheapest delivery option
- Add delivery cost as separate line item in order totals
- Create delivery cost reports for agents
- Implement surge pricing during peak hours
