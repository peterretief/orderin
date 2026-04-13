from django.core.management.base import BaseCommand
from market.models import Product, ProductCategory
from users.models import MarketAgent, CustomUser


class Command(BaseCommand):
    help = 'Delete all products and create new ones matching the available images'

    def handle(self, *args, **options):
        # Delete all existing products
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Deleted all existing products'))

        # Get or create a default market agent for these products
        market_user = CustomUser.objects.filter(user_type='market_agent').first()
        if not market_user:
            market_user = CustomUser.objects.create_user(
                username='admin_market',
                password='password',
                user_type='market_agent',
                first_name='Admin',
                last_name='Market',
                shop_name='Main Market'
            )
            self.stdout.write(f'  ✓ Created market user: {market_user.username}')
        
        market_agent = MarketAgent.objects.filter(user=market_user).first()
        if not market_agent:
            market_agent = MarketAgent.objects.create(user=market_user)
            self.stdout.write(f'  ✓ Created market agent for: {market_user.shop_name}')
        
        self.stdout.write(f'Using market agent: {market_user.shop_name}')

        # Create or get categories
        categories = {
            'Meat': ProductCategory.objects.get_or_create(name='Meat')[0],
            'Fruits': ProductCategory.objects.get_or_create(name='Fruits')[0],
            'Vegetables': ProductCategory.objects.get_or_create(name='Vegetables')[0],
            'Dairy': ProductCategory.objects.get_or_create(name='Dairy')[0],
            'Grains': ProductCategory.objects.get_or_create(name='Grains')[0],
        }

        # Product data: (image_file, name, category, price, description)
        products_data = [
            ('beef.jpg', 'Beef Steak', 'Meat', 12.99, 'Premium quality beef steak'),
            ('chicken.jpg', 'Chicken Breast', 'Meat', 8.99, 'Fresh chicken breast fillets'),
            ('pork.jpg', 'Pork Chops', 'Meat', 10.99, 'Tender pork chops'),
            ('turkey.jpg', 'Turkey Breast', 'Meat', 9.99, 'Lean turkey breast meat'),
            ('ground.jpg', 'Ground Meat', 'Meat', 7.99, 'Ground beef for cooking'),
            ('salmon.jpg', 'Salmon Fillet', 'Meat', 14.99, 'Wild-caught salmon fillet'),
            ('shrimp.jpg', 'Shrimp', 'Meat', 11.99, 'Fresh Gulf shrimp'),
            
            ('mango.jpg', 'Mango', 'Fruits', 2.99, 'Sweet and juicy mango'),
            ('blueberries.jpg', 'Blueberries', 'Fruits', 5.99, 'Fresh blueberries'),
            ('grapes.jpg', 'Grapes', 'Fruits', 3.99, 'Sweet red grapes'),
            ('peaches.jpg', 'Peaches', 'Fruits', 3.49, 'Ripe peaches'),
            ('pineapple.jpg', 'Pineapple', 'Fruits', 4.99, 'Fresh pineapple'),
            ('strawberries.jpg', 'Strawberries', 'Fruits', 4.99, 'Fresh strawberries'),
            ('watermelon.jpg', 'Watermelon', 'Fruits', 6.99, 'Fresh watermelon'),
            
            ('broccoli.jpg', 'Broccoli', 'Vegetables', 2.49, 'Fresh broccoli florets'),
            ('bell.jpg', 'Bell Pepper', 'Vegetables', 2.99, 'Colorful bell peppers'),
            ('cucumber.jpg', 'Cucumber', 'Vegetables', 1.99, 'Fresh cucumbers'),
            ('lettuce.jpg', 'Lettuce', 'Vegetables', 2.49, 'Crisp lettuce'),
            ('onions.jpg', 'Onions', 'Vegetables', 1.99, 'Fresh onions'),
            ('spinach.jpg', 'Spinach', 'Vegetables', 3.49, 'Fresh spinach'),
            ('zucchini.jpg', 'Zucchini', 'Vegetables', 2.49, 'Fresh zucchini'),
            ('garlic.jpg', 'Garlic', 'Vegetables', 1.49, 'Fresh garlic bulbs'),
            ('corn.jpg', 'Corn', 'Vegetables', 2.99, 'Fresh corn on the cob'),
            
            ('mozzarella.jpg', 'Mozzarella Cheese', 'Dairy', 5.99, 'Fresh mozzarella'),
            ('cottage.jpg', 'Cottage Cheese', 'Dairy', 4.99, 'Creamy cottage cheese'),
            
            ('barley.jpg', 'Barley', 'Grains', 3.99, 'Pearl barley grains'),
            ('oats.jpg', 'Oats', 'Grains', 4.49, 'Rolled oats'),
            ('flour.jpg', 'Flour', 'Grains', 3.49, 'All-purpose flour'),
            ('whole.jpg', 'Whole Wheat', 'Grains', 3.99, 'Whole wheat grains'),
            ('pasta.jpg', 'Pasta', 'Grains', 2.99, 'Pasta noodles'),
        ]

        created_count = 0
        for image_file, name, category_name, price, description in products_data:
            sku = image_file.replace('.jpg', '').upper()
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                sku=sku,
                image=f'products/{image_file}',
                category=categories[category_name],
                market_agent=market_agent,
                quantity_available=100,
                unit='each',
                is_available=True
            )
            created_count += 1
            self.stdout.write(f'  ✓ {name} ({image_file})')

        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {created_count} new products'))
