from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from users.models import CustomUser, ServiceAgent, MarketAgent
from market.models import ProductCategory, Product
from orders.models import Order, OrderItem, OrderServiceAgent
from agents.models import ServicePrice, ServiceAvailability
from billing.models import UserBalance, BillingTransaction, BillingPlan


class Command(BaseCommand):
    help = 'Create additional comprehensive data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating additional users and data...')
        
        # Create more subscribers
        self.create_more_subscribers(10)
        
        # Create more market agents with diverse products
        self.create_more_market_agents(5)
        
        # Create more service agents
        self.create_more_service_agents(4)
        
        # Create more products in each category
        self.create_diverse_products()
        
        # Create orders for testing
        self.create_more_orders(20)
        
        # Update balances for new subscribers
        self.update_balances()
        
        self.stdout.write(self.style.SUCCESS('✓ Additional data created successfully!'))

    def create_more_subscribers(self, count):
        """Create more subscriber users"""
        for i in range(4, 4 + count):
            user, created = CustomUser.objects.get_or_create(
                username=f'subscriber{i}',
                defaults={
                    'email': f'subscriber{i}@example.com',
                    'user_type': 'subscriber',
                    'first_name': f'Customer',
                    'last_name': f'{i}',
                    'phone': f'555-100{i % 10}',
                    'address': f'{i}00 Oak Avenue',
                    'city': random.choice(['Townville', 'Cityville', 'Farmville']),
                    'state': random.choice(['CA', 'NY', 'TX', 'FL']),
                    'zip_code': f'9000{i % 10}',
                }
            )
            if created:
                user.set_password('password')
                user.save()
                self.stdout.write(f'  ✓ Created subscriber{i}')

    def create_more_market_agents(self, count):
        """Create more market agents"""
        for i in range(3, 3 + count):
            user, created = CustomUser.objects.get_or_create(
                username=f'market_agent{i}',
                defaults={
                    'email': f'market_agent{i}@example.com',
                    'user_type': 'market_agent',
                    'first_name': f'vendor',
                    'last_name': f'Store {i}',
                    'phone': f'555-000{i}',
                    'shop_name': f'Shop #{i} - {random.choice(["Organic", "Fresh", "Premium", "Local"])} Market',
                    'shop_description': f'Quality products delivered fresh to your door',
                    'address': f'{i}00 Main Street',
                    'city': random.choice(['Farmville', 'Village', 'Suburb']),
                }
            )
            if created:
                user.set_password('password')
                user.save()
                MarketAgent.objects.get_or_create(user=user, defaults={'is_active': True})
                self.stdout.write(f'  ✓ Created market_agent{i}')

    def create_more_service_agents(self, count):
        """Create more delivery and catering agents"""
        service_types = [
            ('delivery', 'Quick Delivery #{num}', 'Car'),
            ('delivery', 'Express Courier #{num}', 'Motorcycle'),
            ('catering', 'Chef Hub #{num}', None),
            ('catering', 'Party Catering #{num}', None),
        ]
        
        for idx, (service_type, name_template, vehicle) in enumerate(service_types):
            i = idx + 1
            username = f'{service_type[0]}_agent{i}' if service_type == 'delivery' else f'caterer{i + 1}'
            
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'user_type': 'delivery_person' if service_type == 'delivery' else 'caterer',
                    'first_name': 'Agent',
                    'last_name': f'{i}',
                    'phone': f'555-{300 + i}{i}{i}',
                    'service_name': name_template.format(num=i),
                    'service_description': f'Professional {service_type} service provider',
                }
            )
            
            if created:
                user.set_password('password')
                user.save()
                
                service_agent, _ = ServiceAgent.objects.get_or_create(
                    user=user,
                    defaults={
                        'service_type': service_type,
                        'is_active': True,
                        'rating': round(random.uniform(4.0, 5.0), 1),
                        'specialty': random.choice(['Italian', 'Asian', 'Mexican', 'Continental']) if service_type == 'catering' else vehicle,
                        'vehicle_type': vehicle,
                        'max_weight_capacity': 50.0 if service_type == 'delivery' else None,
                    }
                )
                
                # Create pricing
                if service_type == 'delivery':
                    ServicePrice.objects.get_or_create(
                        service_agent=service_agent,
                        defaults={
                            'base_price': round(random.uniform(3.0, 8.0), 2),
                            'price_per_km': round(random.uniform(1.0, 2.0), 2),
                        }
                    )
                else:  # catering
                    ServicePrice.objects.get_or_create(
                        service_agent=service_agent,
                        defaults={
                            'base_price': round(random.uniform(100.0, 300.0), 2),
                            'price_per_item': round(random.uniform(3.0, 8.0), 2),
                        }
                    )
                
                # Create availability
                for day in range(7):
                    start_hour = random.choice(['08', '09', '10'])
                    end_hour = random.choice(['18', '19', '20'])
                    ServiceAvailability.objects.get_or_create(
                        service_agent=service_agent,
                        day_of_week=day,
                        start_time=f'{start_hour}:00:00',
                        defaults={
                            'end_time': f'{end_hour}:00:00',
                            'is_available': random.choice([True, True, False]),
                        }
                    )
                
                self.stdout.write(f'  ✓ Created {service_type} agent: {username}')

    def create_diverse_products(self):
        """Create diverse products across categories"""
        products_data = [
            # Vegetables
            ('Vegetables', [
                ('Spinach', 'Fresh organic spinach', 3.50),
                ('Broccoli', 'Green broccoli florets', 2.99),
                ('Bell Peppers', 'Mixed color peppers', 4.50),
                ('Lettuce', 'Romaine lettuce', 2.50),
                ('Cucumber', 'Fresh cucumber', 1.99),
                ('Zucchini', 'Green zucchini', 3.00),
                ('Garlic', 'Fresh garlic bulbs', 2.00),
                ('Onions', 'Yellow onions', 1.50),
            ]),
            # Fruits
            ('Fruits', [
                ('Oranges', 'Fresh oranges', 5.00),
                ('Mango', 'Tropical mangoes', 6.50),
                ('Strawberries', 'Fresh strawberries', 7.99),
                ('Blueberries', 'Premium blueberries', 8.50),
                ('Grapes', 'Green grapes', 4.50),
                ('Watermelon', 'Sweet watermelon', 8.00),
                ('Pineapple', 'Fresh pineapple', 5.50),
                ('Peaches', 'Fresh peaches', 4.99),
            ]),
            # Dairy
            ('Dairy', [
                ('Yogurt', 'Greek yogurt', 4.50),
                ('Butter', 'Salted butter', 6.00),
                ('Mozzarella', 'Fresh mozzarella', 7.50),
                ('Cream Cheese', 'Philadelphia cream cheese', 5.00),
                ('Sour Cream', 'Sour cream', 3.50),
                ('Eggs', 'Dozen eggs', 5.99),
                ('Cottage Cheese', 'Low fat cottage cheese', 4.00),
            ]),
            # Grains
            ('Grains', [
                ('Pasta', 'Italian pasta', 2.00),
                ('Whole Wheat Bread', 'Organic bread', 4.00),
                ('Oats', 'Rolled oats', 3.50),
                ('Flour', 'All purpose flour', 3.00),
                ('Corn', 'Fresh corn', 2.50),
                ('Barley', 'Pearl barley', 2.50),
            ]),
            # Meat
            ('Meat', [
                ('Ground Beef', 'Lean ground beef', 12.00),
                ('Turkey Breast', 'Fresh turkey breast', 10.00),
                ('Salmon', 'Atlantic salmon', 18.00),
                ('Chicken Thighs', 'Chicken thighs', 8.00),
                ('Pork Chops', 'Pork chops', 9.50),
                ('Shrimp', 'Fresh shrimp', 16.00),
                ('Beef Steak', 'NY Steak', 20.00),
            ]),
        ]
        
        category_obj_map = {
            cat.name: cat for cat in ProductCategory.objects.all()
        }
        
        market_agents = list(MarketAgent.objects.all())
        
        if not market_agents:
            self.stdout.write(self.style.WARNING('  ⚠ No market agents found'))
            return
        
        product_count = 0
        for category_name, products_list in products_data:
            if category_name not in category_obj_map:
                continue
            
            category = category_obj_map[category_name]
            
            for product_name, description, price in products_list:
                # Create this product for each market agent
                for market_agent in market_agents:
                    sku = f'{product_name.lower().replace(" ", "_")}_{market_agent.id}'
                    Product.objects.get_or_create(
                        sku=sku,
                        market_agent=market_agent,
                        defaults={
                            'name': product_name,
                            'description': description,
                            'price': price,
                            'unit': 'kg' if category_name in ['Vegetables', 'Fruits', 'Meat'] else 'unit',
                            'category': category,
                            'quantity_available': random.randint(20, 100),
                            'is_available': random.choice([True, True, True, False]),
                        }
                    )
                    product_count += 1
        
        self.stdout.write(f'  ✓ Created {product_count} products')

    def create_more_orders(self, count):
        """Create multiple diverse orders"""
        subscribers = list(CustomUser.objects.filter(user_type='subscriber'))
        products = list(Product.objects.filter(is_available=True))
        service_agents = list(ServiceAgent.objects.all())
        
        if not subscribers or not products:
            self.stdout.write(self.style.WARNING('  ⚠ Not enough data to create orders'))
            return
        
        for i in range(count):
            subscriber = random.choice(subscribers)
            status = random.choice(['pending', 'processing', 'delivered', 'cancelled'])
            
            order = Order.objects.create(
                subscriber=subscriber,
                status=status,
            )
            
            # Add 2-5 items per order
            num_items = random.randint(2, 5)
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price,
                )
            
            # Maybe add a service agent (50% chance)
            if random.choice([True, False]) and service_agents:
                service = random.choice(service_agents)
                price = service.servicepricing.base_price if hasattr(service, 'servicepricing') else random.uniform(5, 50)
                OrderServiceAgent.objects.create(
                    order=order,
                    service_agent=service,
                    service_type=service.service_type,
                    price=round(price, 2),
                )
            
            order.calculate_total()
            
            # Set timestamps for diversity
            if status == 'delivered':
                order.delivered_at = timezone.now() - timedelta(days=random.randint(1, 30))
            
            order.save()
        
        self.stdout.write(f'  ✓ Created {count} orders')

    def update_balances(self):
        """Update balances for all subscribers"""
        subscribers = CustomUser.objects.filter(user_type='subscriber')
        for subscriber in subscribers:
            balance, created = UserBalance.objects.get_or_create(
                user=subscriber,
                defaults={'balance': round(random.uniform(100, 1000), 2)}
            )
            self.stdout.write(f'  ✓ Updated balance for {subscriber.username}')
