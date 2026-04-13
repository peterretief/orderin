"""
Management command to initialize delivery pricing tiers and surcharges.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from delivery.models import (
    DeliveryMethod,
    DeliveryPricingTier,
    WeightBasedPricing,
    TempControlPricing,
)


class Command(BaseCommand):
    help = 'Initialize delivery pricing tiers and surcharge rules'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up delivery pricing...'))
        
        with transaction.atomic():
            self._setup_pricing_tiers()
            self._setup_weight_surcharges()
            self._setup_temp_control_surcharges()
        
        self.stdout.write(self.style.SUCCESS('Delivery pricing setup complete!'))
    
    def _setup_pricing_tiers(self):
        """Setup distance-based pricing tiers for each delivery method."""
        
        self.stdout.write('Setting up pricing tiers...')
        
        # Get or create home delivery method
        home_delivery, _ = DeliveryMethod.objects.get_or_create(
            name='home_delivery',
            defaults={
                'code': 'HOME_DEL',
                'description': 'Home delivery service',
                'method_type': 'delivery',
            }
        )
        
        # Setup home delivery tiers
        home_tiers = [
            {'min': 0, 'max': 5, 'base': 50, 'per_km': 5},
            {'min': 5, 'max': 15, 'base': 75, 'per_km': 3},
            {'min': 15, 'max': 30, 'base': 120, 'per_km': 2},
            {'min': 30, 'max': 999999, 'base': 180, 'per_km': 1.50},
        ]
        
        for tier_data in home_tiers:
            DeliveryPricingTier.objects.update_or_create(
                delivery_method=home_delivery,
                min_distance=Decimal(str(tier_data['min'])),
                max_distance=Decimal(str(tier_data['max'])),
                defaults={
                    'base_price': Decimal(str(tier_data['base'])),
                    'price_per_unit_distance': Decimal(str(tier_data['per_km'])),
                    'distance_unit': 'km',
                    'is_active': True,
                }
            )
            self.stdout.write(f"  ✓ Home delivery {tier_data['min']}-{tier_data['max']}km tier: R{tier_data['base']} + R{tier_data['per_km']}/km")
        
        # Setup collection point tiers
        collection_point, _ = DeliveryMethod.objects.get_or_create(
            name='collection_point',
            defaults={
                'code': 'COLL_PT',
                'description': 'Customer collection from collection point',
                'method_type': 'collection_point',
            }
        )
        
        collection_tiers = [
            {'min': 0, 'max': 999999, 'base': 30, 'per_km': 0},
        ]
        
        for tier_data in collection_tiers:
            DeliveryPricingTier.objects.update_or_create(
                delivery_method=collection_point,
                min_distance=Decimal(str(tier_data['min'])),
                max_distance=Decimal(str(tier_data['max'])),
                defaults={
                    'base_price': Decimal(str(tier_data['base'])),
                    'price_per_unit_distance': Decimal(str(tier_data['per_km'])),
                    'distance_unit': 'km',
                    'is_active': True,
                }
            )
            self.stdout.write(f"  ✓ Collection point tier: R{tier_data['base']}")
        
        # Setup customer collection (pickup)
        customer_collection, _ = DeliveryMethod.objects.get_or_create(
            name='collection',
            defaults={
                'code': 'CUST_COLL',
                'description': 'Customer collection from store',
                'method_type': 'collection',
            }
        )
        
        DeliveryPricingTier.objects.update_or_create(
            delivery_method=customer_collection,
            min_distance=Decimal('0'),
            max_distance=Decimal('999999'),
            defaults={
                'base_price': Decimal('0'),
                'price_per_unit_distance': Decimal('0'),
                'distance_unit': 'km',
                'is_active': True,
            }
        )
        self.stdout.write(f"  ✓ Customer collection (free pickup)")
    
    def _setup_weight_surcharges(self):
        """Setup weight-based surcharges."""
        
        self.stdout.write('Setting up weight surcharges...')
        
        weight_surcharges = [
            {'min': 0, 'max': 5, 'percent': 0, 'fixed': 0},  # Standard
            {'min': 5, 'max': 15, 'percent': 15, 'fixed': 20},  # Heavy items
            {'min': 15, 'max': 30, 'percent': 25, 'fixed': 50},  # Very heavy
            {'min': 30, 'max': 999999, 'percent': 35, 'fixed': 100},  # Oversized
        ]
        
        for surcharge_data in weight_surcharges:
            WeightBasedPricing.objects.update_or_create(
                min_weight_kg=Decimal(str(surcharge_data['min'])),
                max_weight_kg=Decimal(str(surcharge_data['max'])),
                defaults={
                    'surcharge_percentage': Decimal(str(surcharge_data['percent'])),
                    'surcharge_fixed': Decimal(str(surcharge_data['fixed'])),
                    'applies_to_all_methods': True,
                    'is_active': True,
                }
            )
            self.stdout.write(
                f"  ✓ {surcharge_data['min']}-{surcharge_data['max']}kg: "
                f"{surcharge_data['percent']}% + R{surcharge_data['fixed']}"
            )
    
    def _setup_temp_control_surcharges(self):
        """Setup temperature control surcharges."""
        
        self.stdout.write('Setting up temperature control surcharges...')
        
        temp_surcharges = [
            {'storage': 'frozen', 'percent': 30, 'fixed': 75},
            {'storage': 'refrigerated', 'percent': 20, 'fixed': 50},
            {'storage': 'ambient', 'percent': 0, 'fixed': 0},  # No surcharge
            {'storage': 'dry', 'percent': 10, 'fixed': 25},
        ]
        
        for surcharge_data in temp_surcharges:
            TempControlPricing.objects.update_or_create(
                storage_type=surcharge_data['storage'],
                defaults={
                    'surcharge_percentage': Decimal(str(surcharge_data['percent'])),
                    'surcharge_fixed': Decimal(str(surcharge_data['fixed'])),
                    'requires_vehicle_capability': True,
                    'is_active': True,
                }
            )
            self.stdout.write(
                f"  ✓ {surcharge_data['storage']}: "
                f"{surcharge_data['percent']}% + R{surcharge_data['fixed']}"
            )
