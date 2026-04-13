"""
Management command to set up initial delivery methods.
Run: python manage.py setup_delivery_methods
"""
from django.core.management.base import BaseCommand
from delivery.models import DeliveryMethod


class Command(BaseCommand):
    help = 'Set up initial delivery methods'

    def handle(self, *args, **options):
        methods_data = [
            {
                'name': 'Customer Pickup',
                'code': 'CUSTOMER_PICKUP',
                'method_type': 'collection',
                'description': 'Customer collects order from designated pickup location',
                'is_active': True,
            },
            {
                'name': 'Standard Home Delivery',
                'code': 'HOME_DELIVERY',
                'method_type': 'delivery',
                'description': 'Our delivery agent will deliver to your home address',
                'is_active': True,
            },
            {
                'name': 'Collection Point Delivery',
                'code': 'COLLECTION_POINT',
                'method_type': 'collection_point',
                'description': 'Order will be sent to a nearby shop or collection point',
                'is_active': True,
            },
            {
                'name': 'Express Same-Day Delivery',
                'code': 'EXPRESS_DELIVERY',
                'method_type': 'delivery',
                'description': 'Fast delivery within the same day (available for selected areas)',
                'is_active': True,
            },
        ]

        created_count = 0
        for method_data in methods_data:
            method, created = DeliveryMethod.objects.get_or_create(
                code=method_data['code'],
                defaults=method_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {method.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⟳ Already exists: {method.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Setup complete! Created {created_count} delivery methods.')
        )
