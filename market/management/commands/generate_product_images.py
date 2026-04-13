from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import requests
import time
from market.models import Product, ProductCategory

class Command(BaseCommand):
    help = 'Generate product images using AI (pollinations.ai)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing images',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit the number of images to generate',
        )

    def handle(self, *args, **options):
        self.stdout.write('Generating AI product images...')
        
        force = options['force']
        limit = options['limit']
        
        if force:
            products = Product.objects.all()
        else:
            products = Product.objects.filter(image='')
            
        if limit > 0:
            products = products[:limit]
            
        count = 0
        total = products.count()
        
        for i, product in enumerate(products):
            try:
                self.stdout.write(f'[{i+1}/{total}] Generating image for {product.name}...')
                image_data = self.generate_ai_image(product)
                
                if image_data:
                    filename = f'{product.sku}.jpg'
                    product.image.save(filename, ContentFile(image_data), save=True)
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Generated image for {product.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ! Failed to generate image for {product.name}, skipping'))
                
                # Small delay to be polite to the API
                time.sleep(1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error for {product.name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Generated {count} product images'))

    def generate_ai_image(self, product):
        """Generate a product image using pollinations.ai"""
        # Improved prompt for better product shots
        category_name = product.category.name if product.category else ''
        prompt = f"high quality studio photography of {product.name} {category_name}, professional lighting, white background, 4k, sharp focus"
        
        # Pollinations.ai URL format
        encoded_prompt = prompt.replace(' ', '%20')
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=600&model=flux&nologo=true"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                return response.content
            else:
                self.stdout.write(self.style.ERROR(f'  ! API returned status {response.status_code} or invalid content type {response.headers.get("content-type")}'))
                return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ! Request error: {str(e)}'))
            return None
