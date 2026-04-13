#!/usr/bin/env python
"""Test image display."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from users.models import CustomUser

# Create test client
client = Client()
user = CustomUser.objects.filter(user_type='subscriber').first()
client.force_login(user)

# Get shop page
response = client.get('/shop/browse/')
html = response.content.decode()

# Count img tags
import re
img_tags = re.findall(r'<img[^>]+src="([^"]+)"', html)
print(f"Found {len(img_tags)} img tags in shop page")

if img_tags:
    print("\nFirst 5 image src values:")
    for i, src in enumerate(img_tags[:5]):
        print(f"  {i+1}. {src}")
        
    # Test each image URL
    print("\n\nTesting image URLs:")
    for src in img_tags[:3]:
        img_response = client.get(src)
        print(f"{src}")
        print(f"  Status: {img_response.status_code}")
        print(f"  Content-Type: {img_response.get('Content-Type', 'N/A')}")
        print(f"  Size: {len(img_response.content)} bytes")
else:
    print("No img tags found!")
    
# Check if API returns images
print("\n\n API Test:")
api_response = client.get('/api/market/products/')
import json
data = json.loads(api_response.content)
if data:
    p = data[0]
    print(f"First product image from API: {p.get('image')}")
