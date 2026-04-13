"""
Delivery costing utility functions.
Calculates delivery costs based on multiple factors: weight, temperature, distance, etc.
"""

from decimal import Decimal
from .models import (
    DeliveryPricingTier,
    WeightBasedPricing,
    TempControlPricing,
    DeliveryCost,
    OrderDelivery,
)


class DeliveryCostCalculator:
    """Calculate delivery costs based on order and delivery details."""
    
    def __init__(self, order_delivery, distance_km=None, actual_weight_kg=None):
        """
        Initialize calculator with order delivery details.
        
        Args:
            order_delivery: OrderDelivery instance
            distance_km: Delivery distance in kilometers (optional)
            actual_weight_kg: Actual weight of items in kg (optional)
        """
        self.order_delivery = order_delivery
        self.order = order_delivery.order
        self.delivery_method = order_delivery.delivery_method
        self.distance_km = distance_km or Decimal('0')
        self.actual_weight_kg = actual_weight_kg or self._calculate_order_weight()
        self.cost_breakdown = {
            'base_price': Decimal('0'),
            'distance_charge': Decimal('0'),
            'weight_surcharge': Decimal('0'),
            'temp_control_surcharge': Decimal('0'),
            'signature_required_surcharge': Decimal('0'),
            'rush_delivery_surcharge': Decimal('0'),
            'other_surcharges': Decimal('0'),
            'discount_percentage': Decimal('0'),
            'discount_amount': Decimal('0'),
            'tax_percentage': Decimal('0'),
            'tax_amount': Decimal('0'),
        }
    
    def _calculate_order_weight(self):
        """Calculate total weight of items in order."""
        total_kg = Decimal('0')
        for item in self.order.items.all():
            if hasattr(item, 'product') and hasattr(item.product, 'weight_kg'):
                total_kg += Decimal(str(item.product.weight_kg)) * item.quantity
        return total_kg
    
    def get_base_price(self):
        """Get base price from pricing tier based on distance."""
        try:
            # Find matching pricing tier
            tier = DeliveryPricingTier.objects.filter(
                delivery_method=self.delivery_method,
                min_distance__lte=self.distance_km,
                max_distance__gte=self.distance_km,
                is_active=True
            ).first()
            
            if not tier:
                # Use highest tier if distance exceeds all tiers
                tier = DeliveryPricingTier.objects.filter(
                    delivery_method=self.delivery_method,
                    is_active=True
                ).order_by('-max_distance').first()
            
            if tier:
                base = tier.base_price
                # Add per-km charge
                distance_beyond_base = self.distance_km - tier.min_distance
                if distance_beyond_base > 0 and tier.price_per_unit_distance:
                    base += distance_beyond_base * Decimal(str(tier.price_per_unit_distance))
                
                # Store distance charge separately
                self.cost_breakdown['distance_charge'] = Decimal(str(tier.price_per_unit_distance)) * distance_beyond_base if distance_beyond_base > 0 else Decimal('0')
                
                return base
        except Exception:
            pass
        
        return Decimal('10')  # Default minimum base price
    
    def get_weight_surcharge(self):
        """Calculate surcharge based on weight."""
        surcharge = Decimal('0')
        
        # Find applicable weight-based pricing
        weight_pricings = WeightBasedPricing.objects.filter(
            min_weight_kg__lte=self.actual_weight_kg,
            max_weight_kg__gte=self.actual_weight_kg,
            is_active=True
        )
        
        # Filter by delivery method if specified
        for pricing in weight_pricings:
            if pricing.applies_to_all_methods or pricing.delivery_methods.filter(id=self.delivery_method.id).exists():
                # Apply surcharges
                if pricing.surcharge_percentage > 0:
                    surcharge += self.cost_breakdown['base_price'] * (Decimal(str(pricing.surcharge_percentage)) / Decimal('100'))
                if pricing.surcharge_fixed > 0:
                    surcharge += Decimal(str(pricing.surcharge_fixed))
        
        self.cost_breakdown['weight_surcharge'] = surcharge
        return surcharge
    
    def get_temp_control_surcharge(self):
        """Calculate surcharge for temperature-controlled delivery."""
        surcharge = Decimal('0')
        
        # Check if order requires temperature control
        if self.order_delivery.cold_chain_requirement:
            storage_type = self.order_delivery.cold_chain_requirement.storage_type
            
            try:
                temp_pricing = TempControlPricing.objects.get(
                    storage_type=storage_type,
                    is_active=True
                )
                
                # Apply surcharges
                if temp_pricing.surcharge_percentage > 0:
                    surcharge += self.cost_breakdown['base_price'] * (Decimal(str(temp_pricing.surcharge_percentage)) / Decimal('100'))
                if temp_pricing.surcharge_fixed > 0:
                    surcharge += Decimal(str(temp_pricing.surcharge_fixed))
            except TempControlPricing.DoesNotExist:
                pass
        
        self.cost_breakdown['temp_control_surcharge'] = surcharge
        return surcharge
    
    def add_surcharges(self, signature_required=False, rush_delivery=False, other_amount=Decimal('0')):
        """Add additional surcharges."""
        if signature_required and self.order_delivery.signature_required:
            self.cost_breakdown['signature_required_surcharge'] = Decimal('50')  # Fixed amount
        
        if rush_delivery:
            self.cost_breakdown['rush_delivery_surcharge'] = self.cost_breakdown['base_price'] * Decimal('0.25')  # 25% surcharge
        
        if other_amount > 0:
            self.cost_breakdown['other_surcharges'] = Decimal(str(other_amount))
    
    def apply_discount(self, discount_percentage=0, discount_amount=0):
        """Apply discounts to the cost."""
        if discount_percentage > 0:
            self.cost_breakdown['discount_percentage'] = Decimal(str(discount_percentage))
        if discount_amount > 0:
            self.cost_breakdown['discount_amount'] = Decimal(str(discount_amount))
    
    def apply_tax(self, tax_percentage=15):
        """Apply tax percentage."""
        self.cost_breakdown['tax_percentage'] = Decimal(str(tax_percentage))
    
    def calculate(self):
        """Calculate total delivery cost."""
        # Get base price
        base = self.get_base_price()
        self.cost_breakdown['base_price'] = base
        
        # Add surcharges
        total = base
        total += self.get_weight_surcharge()
        total += self.get_temp_control_surcharge()
        total += self.cost_breakdown.get('signature_required_surcharge', Decimal('0'))
        total += self.cost_breakdown.get('rush_delivery_surcharge', Decimal('0'))
        total += self.cost_breakdown.get('other_surcharges', Decimal('0'))
        
        # Apply discounts
        discount_amount = self.cost_breakdown.get('discount_amount', Decimal('0'))
        discount_percentage = self.cost_breakdown.get('discount_percentage', Decimal('0'))
        
        if discount_percentage > 0:
            discount_amount += total * (discount_percentage / Decimal('100'))
        
        subtotal = max(total - discount_amount, Decimal('0'))
        self.cost_breakdown['subtotal'] = subtotal
        
        # Apply tax
        tax_percentage = self.cost_breakdown.get('tax_percentage', Decimal('0'))
        tax_amount = subtotal * (tax_percentage / Decimal('100')) if tax_percentage > 0 else Decimal('0')
        
        self.cost_breakdown['tax_amount'] = tax_amount
        total_cost = subtotal + tax_amount
        
        return {
            'subtotal': subtotal,
            'total_cost': total_cost,
            'breakdown': self.cost_breakdown
        }
    
    def save_cost(self, tax_percentage=15):
        """Calculate and save delivery cost to database."""
        self.apply_tax(tax_percentage)
        result = self.calculate()
        
        # Create or update DeliveryCost record
        cost, created = DeliveryCost.objects.update_or_create(
            order_delivery=self.order_delivery,
            defaults={
                'base_price': self.cost_breakdown['base_price'],
                'distance_km': self.distance_km,
                'distance_charge': self.cost_breakdown['distance_charge'],
                'actual_weight_kg': self.actual_weight_kg,
                'weight_surcharge': self.cost_breakdown['weight_surcharge'],
                'temp_control_surcharge': self.cost_breakdown['temp_control_surcharge'],
                'signature_required_surcharge': self.cost_breakdown.get('signature_required_surcharge', Decimal('0')),
                'rush_delivery_surcharge': self.cost_breakdown.get('rush_delivery_surcharge', Decimal('0')),
                'other_surcharges': self.cost_breakdown.get('other_surcharges', Decimal('0')),
                'discount_percentage': self.cost_breakdown.get('discount_percentage', Decimal('0')),
                'discount_amount': self.cost_breakdown.get('discount_amount', Decimal('0')),
                'tax_percentage': self.cost_breakdown.get('tax_percentage', Decimal('0')),
                'tax_amount': self.cost_breakdown['tax_amount'],
                'subtotal': result['subtotal'],
                'total_cost': result['total_cost'],
            }
        )
        
        return cost


def calculate_delivery_cost(order_delivery, distance_km=None, actual_weight_kg=None, tax_percentage=15):
    """
    Convenience function to calculate delivery cost.
    
    Args:
        order_delivery: OrderDelivery instance
        distance_km: Optional delivery distance in km
        actual_weight_kg: Optional actual weight in kg
        tax_percentage: Tax rate percentage (default 15%)
    
    Returns:
        DeliveryCost instance with calculated costs
    """
    calculator = DeliveryCostCalculator(order_delivery, distance_km, actual_weight_kg)
    return calculator.save_cost(tax_percentage)
