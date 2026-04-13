# Development Guidelines

Standards and best practices for Order In development.

## Code Style

### Python (PEP 8)

```python
# ✅ Good
def calculate_delivery_cost(distance_km, base_rate=50):
    """Calculate delivery cost based on distance.
    
    Args:
        distance_km: Distance in kilometers
        base_rate: Base delivery rate
        
    Returns:
        float: Total delivery cost
    """
    return base_rate + (distance_km * 5.50)


# ❌ Bad
def cost(d,r=50):
    return r+(d*5.50)
```

### Django Models

```python
# ✅ Good
class Order(models.Model):
    """Order model for customer purchases."""
    
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"
```

### Django Views

```python
# ✅ Good
@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Edit user profile information.
    
    GET: Display profile form
    POST: Update profile data
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Update user
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(initial={...})
    
    return render(request, 'profile.html', {'form': form})
```

### HTML/Templates

```html
<!-- ✅ Good -->
{% extends 'dashboards/base.html' %}

{% block title %}Page Title - Order In{% endblock %}

{% block content %}
<div class="container mt-5">
    {% if messages %}
    {% for message in messages %}
    <div class="alert alert-{{ message.tags }}">
        {{ message }}
    </div>
    {% endfor %}
    {% endif %}
    
    <!-- Content here -->
</div>
{% endblock %}
```

## Git Workflow

### Commit Messages

```bash
# ✅ Good
git commit -m "feat: Add profile editing for all user types"
git commit -m "fix: Correct address validation for generic suburbs"
git commit -m "docs: Update README with installation steps"

# ❌ Bad
git commit -m "fix stuff"
git commit -m "updated"
git commit -m "changes"
```

### Branch Naming

```bash
# Feature branches
git checkout -b feature/profile-editing
git checkout -b feature/address-validation

# Bug fix branches
git checkout -b fix/address-geocoding-error
git checkout -b fix/delivery-cost-calculation

# Documentation branches
git checkout -b docs/api-documentation
```

### Pull Request Process

1. Create feature branch from `main`
2. Make commits with clear messages
3. Push to GitHub
4. Create Pull Request with description:
   - What changes were made
   - Why they were made
   - How to test
5. Get code review
6. Merge to main

## Testing

### Unit Tests

```python
# tests/test_models.py
from django.test import TestCase
from users.models import CustomUser

class CustomUserTestCase(TestCase):
    """Test CustomUser model."""
    
    def setUp(self):
        """Create test user."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='subscriber'
        )
    
    def test_user_creation(self):
        """Test user is created correctly."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_type, 'subscriber')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_string_representation(self):
        """Test user string output."""
        expected = f"{self.user.username} (Subscriber)"
        self.assertEqual(str(self.user), expected)
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test users

# Run specific test
python manage.py test users.tests.CustomUserTestCase

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Fixtures

Create test data in `fixtures/`:

```bash
python manage.py dumpdata users > fixtures/users.json
python manage.py loaddata fixtures/users.json
```

## Documentation

### Docstring Format

```python
def calculate_delivery_cost(distance_km, base_rate=50):
    """Calculate delivery cost based on distance.
    
    Uses dynamic pricing based on distance from store to customer
    location. Supports minimum and maximum charges.
    
    Args:
        distance_km (float): Distance in kilometers
        base_rate (float): Base delivery rate in currency
        
    Returns:
        float: Total delivery cost with distance markup
        
    Raises:
        ValueError: If distance_km is negative
        
    Example:
        >>> calculate_delivery_cost(5.2, base_rate=50)
        76.6
    """
    if distance_km < 0:
        raise ValueError("Distance cannot be negative")
    
    return base_rate + (distance_km * 5.50)
```

## Database Migrations

### Creating Migrations

```bash
# Make changes to models.py
nano users/models.py

# Create migration file
python manage.py makemigrations users

# Review migration
nano users/migrations/0003_*.py

# Apply migration
python manage.py migrate
```

### Migration Best Practices

✅ **Do:**
- Create migrations for any model changes
- Review migrations before applying
- Test migrations on dev database
- Write meaningful migration names
- Add data migrations for updates

❌ **Don't:**
- Manual SQL edits to models
- Skip migrations
- Test migrations on production
- Delete migration files

## Performance

### Database Queries

```python
# ❌ Bad - N+1 queries
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)  # Extra query per order

# ✅ Good - Use select_related
orders = Order.objects.select_related('customer')
for order in orders:
    print(order.customer.name)  # No extra queries

# ✅ Good - Use prefetch_related for M2M
orders = Order.objects.prefetch_related('items')
```

### Caching

```python
from django.views.decorators.cache import cache_page

# Cache view for 5 minutes
@cache_page(60 * 5)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
```

## Security

### Authentication

```python
# ✅ Require login
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    return render(request, 'protected.html')

# ✅ Check permissions
@login_required
def agent_only_view(request):
    if request.user.user_type != 'market_agent':
        raise PermissionDenied
    return render(request, 'agent.html')
```

### Form Validation

```python
# ✅ Always validate input
from django import forms

class AddressForm(forms.Form):
    address = forms.CharField(
        max_length=500,
        min_length=5
    )
    city = forms.CharField(max_length=100)
    
    def clean(self):
        cleaned_data = super().clean()
        # Additional validation
        return cleaned_data
```

### SQL Injection Prevention

```python
# ❌ Bad - SQL injection risk
orders = Order.objects.raw(f"SELECT * FROM orders WHERE id = {order_id}")

# ✅ Good - ORM prevents injection
order = Order.objects.get(id=order_id)

# ✅ Good - If raw SQL needed
orders = Order.objects.raw("SELECT * FROM orders WHERE id = %s", [order_id])
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_id):
    """Process an order."""
    logger.info(f"Processing order {order_id}")
    
    try:
        order = Order.objects.get(id=order_id)
        # Process...
        logger.info(f"Order {order_id} processed successfully")
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        raise
    except Exception as e:
        logger.exception(f"Error processing order {order_id}: {str(e)}")
        raise
```

## Debugging

### Django Debug Toolbar

```python
# Install
pip install django-debug-toolbar

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

# Add middleware
MIDDLEWARE = [
    ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Set allowed hosts
INTERNAL_IPS = ['127.0.0.1']
```

### Print Debugging

```python
# Use logging instead of print
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Variable value: {variable}")
logger.info(f"Processing started")
logger.warning(f"Unusual condition detected")
logger.error(f"Error occurred: {error}")
```

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`python manage.py test`)
- [ ] No debug mode (`DEBUG = False`)
- [ ] Secret key is secure
- [ ] Database is configured correctly
- [ ] Static files are collected
- [ ] Email is configured
- [ ] Backup strategy is in place
- [ ] Monitoring is set up
- [ ] HTTPS is enabled
- [ ] Security headers are set
- [ ] Firewall rules are configured

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/intro/install/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
