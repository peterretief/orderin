from django.core.management.base import BaseCommand
from users.models import MarketAgent
from market.models import Product


class Command(BaseCommand):
    help = 'Distribute products across different market agents'

    def handle(self, *args, **options):
        # Get all agents
        agents = list(MarketAgent.objects.all())
        
        if not agents:
            self.stdout.write(self.style.ERROR('No agents found'))
            return
        
        # Get all products currently owned by market_agent3
        source_agent = agents[0]  # market_agent3
        products = list(source_agent.products.all())
        
        self.stdout.write(f'Found {len(products)} products to redistribute')
        self.stdout.write(f'Distributing across {len(agents)} agents\n')
        
        # Distribute products round-robin style
        for idx, product in enumerate(products):
            agent = agents[idx % len(agents)]
            product.market_agent = agent
            product.save()
            self.stdout.write(f'✓ {product.name} → {agent.user.shop_name}')
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n✓ Distribution complete!'))
        self.stdout.write('Summary:')
        for agent in agents:
            count = agent.products.count()
            self.stdout.write(f'  {agent.user.shop_name}: {count} products')
