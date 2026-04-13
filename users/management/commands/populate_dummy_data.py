from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser, ServiceAgent, MarketAgent
from market.models import ProductCategory, Product
from orders.models import Order, OrderItem, OrderServiceAgent
from agents.models import ServicePrice, ServiceAvailability
from billing.models import UserBalance, BillingTransaction, BillingPlan


class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data...')
        
        # Create admin user
        admin = self.create_admin_user()
        
        # Create market agents with products
        market_agents = self.create_market_agents()
        
        # Create subscribers
        subscribers = self.create_subscribers()
        
        # Create service agents (caterers and delivery)
        service_agents = self.create_service_agents()
        
        # Create product categories and products
        self.create_products(market_agents)
        
        # Create orders
        self.create_orders(subscribers, service_agents)
        
        # Create user balances
        self.create_balances(subscribers)
        
        # Create billing plans
        self.create_billing_plans()
        
        self.stdout.write(self.style.SUCCESS('✓ Dummy data created successfully!'))
        self.stdout.write(f'  Admin: admin / password')
        self.stdout.write(f'  Market Agent 1: market_agent1 / password')
        self.stdout.write(f'  Subscriber 1: subscriber1 / password')
        self.stdout.write(f'  Caterer 1: caterer1 / password')
        self.stdout.write(f'  Delivery Person 1: delivery1 / password')

    def create_admin_user(self):
        """Create admin user"""
        admin, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'user_type': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
            }
        )
        if created:
            admin.set_password('password')
            admin.save()
            self.stdout.write('  ✓ Admin user created')
        return admin

    def create_market_agents(self):
        """Create market agents"""
        agents = []
        for i in range(1, 3):
            user, created = CustomUser.objects.get_or_create(
                username=f'market_agent{i}',
                defaults={
                    'email': f'market_agent{i}@example.com',
                    'user_type': 'market_agent',
                    'first_name': f'Market Agent {i}',
                    'last_name': f'Shop {i}',
                    'phone': f'555-000{i}',
                    'shop_name': f'Fresh Produce Shop {i}',
                    'shop_description': f'High quality organic produce from farm {i}',
                    'address': f'{i}00 Main Street',
                    'city': 'Farmville',
                }
            )
            if created:
                user.set_password('password')
                user.save()
            
            market_agent, _ = MarketAgent.objects.get_or_create(
                user=user,
                defaults={'is_active': True}
            )
            agents.append(user)
        
        self.stdout.write(f'  ✓ {len(agents)} market agents created')
        return agents

    def create_subscribers(self):
        """Create subscriber users"""
        subscribers = []
        for i in range(1, 4):
            user, created = CustomUser.objects.get_or_create(
                username=f'subscriber{i}',
                defaults={
                    'email': f'subscriber{i}@example.com',
                    'user_type': 'subscriber',
                    'first_name': f'John',
                    'last_name': f'Subscriber {i}',
                    'phone': f'555-100{i}',
                    'address': f'{i}00 Oak Avenue',
                    'city': 'Townville',
                    'state': 'CA',
                    'zip_code': f'9000{i}',
                }
            )
            if created:
                user.set_password('password')
                user.save()
            
            subscribers.append(user)
        
        self.stdout.write(f'  ✓ {len(subscribers)} subscribers created')
        return subscribers

    def create_service_agents(self):
        """Create service agents (caterers and delivery)"""
        service_agents = []
        
        # Caterers
        for i in range(1, 2):
            user, created = CustomUser.objects.get_or_create(
                username=f'caterer{i}',
                defaults={
                    'email': f'caterer{i}@example.com',
                    'user_type': 'caterer',
                    'first_name': 'Chef',
                    'last_name': f'Caterer {i}',
                    'phone': f'555-200{i}',
                    'service_name': f'Gourmet Catering Co. {i}',
                    'service_description': f'Premium catering for events and parties',
                }
            )
            if created:
                user.set_password('password')
                user.save()
            
            service_agent, _ = ServiceAgent.objects.get_or_create(
                user=user,
                defaults={
                    'service_type': 'catering',
                    'is_active': True,
                    'rating': 4.8,
                    'specialty': 'Italian Cuisine',
                }
            )
            
            # Create pricing for caterer
            ServicePrice.objects.get_or_create(
                service_agent=service_agent,
                defaults={
                    'base_price': 150.00,
                    'price_per_item': 5.00,
                }
            )
            
            service_agents.append(service_agent)
        
        # Delivery people
        for i in range(1, 3):
            user, created = CustomUser.objects.get_or_create(
                username=f'delivery{i}',
                defaults={
                    'email': f'delivery{i}@example.com',
                    'user_type': 'delivery_person',
                    'first_name': 'Driver',
                    'last_name': f'Delivery {i}',
                    'phone': f'555-300{i}',
                    'service_name': f'Quick Delivery #{i}',
                    'service_description': f'Fast and reliable delivery service',
                }
            )
            if created:
                user.set_password('password')
                user.save()
            
            service_agent, _ = ServiceAgent.objects.get_or_create(
                user=user,
                defaults={
                    'service_type': 'delivery',
                    'is_active': True,
                    'rating': 4.9,
                    'vehicle_type': 'Car',
                    'max_weight_capacity': 50.0,
                }
            )
            
            # Create pricing for delivery
            ServicePrice.objects.get_or_create(
                service_agent=service_agent,
                defaults={
                    'base_price': 5.00,
                    'price_per_km': 1.50,
                }
            )
            
            # Create availability slots
            for day in range(7):  # 7 days a week
                ServiceAvailability.objects.get_or_create(
                    service_agent=service_agent,
                    day_of_week=day,
                    start_time='09:00:00',
                    defaults={
                        'end_time': '18:00:00',
                        'is_available': True,
                    }
                )
            
            service_agents.append(service_agent)
        
        self.stdout.write(f'  ✓ {len(service_agents)} service agents created')
        return service_agents

    def create_products(self, market_agents):
        """Create product categories and products"""
        categories_data = [
            ('Vegetables', 'Fresh vegetables'),
            ('Fruits', 'Fresh fruits'),
            ('Dairy', 'Milk, cheese, yogurt'),
            ('Grains', 'Rice, wheat, quinoa'),
            ('Meat', 'Fresh meat and poultry'),
        ]
        
        categories = []
        for name, desc in categories_data:
            category, _ = ProductCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            categories.append(category)
        
        products_data = [
            ('Tomatoes', 'Fresh ripe tomatoes', 3.50, 'kg', 'Vegetables'),
            ('Carrots', 'Organic carrots', 2.00, 'kg', 'Vegetables'),
            ('Apples', 'Red delicious apples', 4.50, 'kg', 'Fruits'),
            ('Bananas', 'Yellow bananas', 1.50, 'kg', 'Fruits'),
            ('Milk', 'Fresh whole milk', 3.25, 'liter', 'Dairy'),
            ('Cheese', 'Cheddar cheese', 8.00, 'kg', 'Dairy'),
            ('Rice', 'White basmati rice', 2.50, 'kg', 'Grains'),
            ('Chicken Breast', 'Fresh chicken breast', 12.00, 'kg', 'Meat'),
        ]
        
        product_count = 0
        for name, desc, price, unit, category_name in products_data:
            category = next(c for c in categories if c.name == category_name)
            for market_agent in market_agents:
                Product.objects.get_or_create(
                    sku=f'{name.lower().replace(" ", "_")}_{market_agent.id}',
                    market_agent=MarketAgent.objects.get(user=market_agent),
                    defaults={
                        'name': name,
                        'description': desc,
                        'price': price,
                        'unit': unit,
                        'category': category,
                        'quantity_available': 100,
                        'is_available': True,
                    }
                )
                product_count += 1
        
        self.stdout.write(f'  ✓ {product_count} products created')

    def create_orders(self, subscribers, service_agents):
        """Create sample orders"""
        products = Product.objects.all()
        
        order_count = 0
        for subscriber in subscribers:
            # Create 2 orders per subscriber
            for _ in range(2):
                order = Order.objects.create(
                    subscriber=subscriber,
                    status='delivered',
                )
                
                # Add random products to order
                for i in range(1, 4):
                    if products.exists():
                        product = products[i % len(products)]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=2,
                            unit_price=product.price,
                        )
                
                # Add random service agents
                if service_agents:
                    service = service_agents[order_count % len(service_agents)]
                    OrderServiceAgent.objects.create(
                        order=order,
                        service_agent=service,
                        service_type=service.service_type,
                        price=50.00 if service.service_type == 'catering' else 10.00,
                    )
                
                order.calculate_total()
                order.delivered_at = timezone.now() - timedelta(days=order_count)
                order.save()
                
                order_count += 1
        
        self.stdout.write(f'  ✓ {order_count} orders created')

    def create_balances(self, subscribers):
        """Create user balances"""
        for subscriber in subscribers:
            UserBalance.objects.get_or_create(
                user=subscriber,
                defaults={'balance': 500.00}
            )
        
        self.stdout.write(f'  ✓ {len(subscribers)} user balances created')

    def create_billing_plans(self):
        """Create billing plans"""
        plans = [
            ('Monthly Subscription', 'Monthly subscription for regular ordering', 'monthly', 49.99),
            ('Per Order', 'Pay as you go per order', 'per_order', 0.00),
        ]
        
        for name, desc, plan_type, amount in plans:
            BillingPlan.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'plan_type': plan_type,
                    'amount': amount,
                    'is_active': True,
                }
            )
        
        self.stdout.write(f'  ✓ {len(plans)} billing plans created')
