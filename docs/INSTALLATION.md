# Installation Guide

Complete setup instructions for Order In application.

## Prerequisites

- Python 3.8+
- pip or conda
- Git
- Virtual environment tool (venv recommended)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/orderin.git
cd orderin
```

### 2. Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Required Variables:**
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/orderin
```

### 5. Run Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### 6. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 7. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Access the application at: **http://localhost:8000**

Access admin panel at: **http://localhost:8000/admin**

## Database Setup

### SQLite (Default - Development)

SQLite is configured by default and requires no additional setup.

```
db.sqlite3  # Created automatically after migrations
```

### PostgreSQL (Production)

Install PostgreSQL and set the database URL:

```bash
# Install psycopg2 driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/orderin

# Run migrations
python manage.py migrate
```

## Creating Test Users

```bash
python manage.py shell
```

```python
from users.models import CustomUser

# Create subscriber
CustomUser.objects.create_user(
    username='john_subscriber',
    email='john@example.com',
    password='testpass123',
    user_type='subscriber',
    first_name='John',
    last_name='Doe'
)

# Create market agent
CustomUser.objects.create_user(
    username='fresh_market',
    email='market@example.com',
    password='testpass123',
    user_type='market_agent',
    shop_name='Fresh Produce Market',
    shop_description='High quality organic produce'
)

# Create delivery person
CustomUser.objects.create_user(
    username='delivery_john',
    email='delivery@example.com',
    password='testpass123',
    user_type='delivery_person',
    first_name='John',
    last_name='Driver'
)
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test market
python manage.py test orders
python manage.py test billing

# Run with verbose output
python manage.py test -v 2

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
```

## Static Files (Production)

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

## Troubleshooting

### Issue: "No module named 'django'"
**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "django.core.exceptions.ImproperlyConfigured"
**Solution:** Ensure `.env` file exists with required variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### Issue: Database migrations fail
**Solution:** Check database connection and try reset
```bash
python manage.py migrate users --fake-initial
python manage.py migrate
```

### Issue: Port 8000 already in use
**Solution:** Use a different port
```bash
python manage.py runserver 8001
```

## Next Steps

- Read [USER_GUIDES.md](USER_GUIDES.md) for application usage
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API endpoints
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines
