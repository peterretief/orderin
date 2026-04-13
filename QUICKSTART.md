# Quick Start Guide

## Prerequisites
- PostgreSQL database (local or remote)
- Python 3.8 or higher
- pip and virtualenv

## Setup Steps

### 1. Create Virtual Environment and Install Dependencies

```bash
cd /opt/orderin
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env

# Edit .env with your database credentials
# For SQLite (development):
# DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/orderin

# Also change:
# DJANGO_SECRET_KEY: Generate a new secure random key
```

### 3. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin User

```bash
python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: admin@example.com
# Password: (choose a strong password)
```

### 5. Start Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

The server will be available at: `http://localhost:8000`

## First Steps After Setup

### Access Admin Panel
- URL: `http://localhost:8000/admin`
- Login with your superuser credentials
- Create billing plans and manage users

### Create Test Data

#### 1. Register Different User Types

Via API:
```bash
# Register Market Agent
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "market_agent1",
    "email": "market@example.com",
    "password": "test123456",
    "password_confirm": "test123456",
    "user_type": "market_agent",
    "phone": "1234567890"
  }'

# Register Subscriber
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "subscriber1",
    "email": "subscriber@example.com",
    "password": "test123456",
    "password_confirm": "test123456",
    "user_type": "subscriber"
  }'

# Register Caterer
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "caterer1",
    "email": "caterer@example.com",
    "password": "test123456",
    "password_confirm": "test123456",
    "user_type": "caterer",
    "phone": "9876543210"
  }'
```

#### 2. Login and Add Products

```bash
# Login as market agent
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "market_agent1",
    "password": "test123456"
  }'
```

#### 3. Subscriber Workflow

```bash
# Login as subscriber
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "subscriber1",
    "password": "test123456"
  }'

# Add funds (requires authentication)
curl -X POST http://localhost:8000/api/billing/balance/add_funds/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{"amount": "1000"}'

# Create order (requires authentication)
curl -X POST http://localhost:8000/api/orders/create_order/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2}
    ],
    "service_agents": [
      {"service_agent_id": 1, "price": 100}
    ],
    "notes": "Please deliver by 6 PM"
  }'
```

## Development Tips

### Useful Commands

```bash
# Create a new Django app
python manage.py startapp app_name

# Check migrations
python manage.py showmigrations

# Run specific migration
python manage.py migrate app_name 0002

# Create test data with shell
python manage.py shell

# Run tests
python manage.py test

# Format code (optional)
pip install black
black .
```

### Project Structure

```
orderin/
├── manage.py                   # Django CLI
├── requirements.txt            # Dependencies
├── .env                        # Environment (don't commit)
├── .env.example               # Template
├── .gitignore                 # Git ignore rules
├── README.md                  # Full documentation
├── QUICKSTART.md             # This file
│
├── config/                    # Django project settings
│   ├── settings.py           # Main settings
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI app
│   └── __init__.py
│
├── users/                     # User management
│   ├── models.py             # User models
│   ├── views.py              # API views
│   ├── serializers.py        # Data serializers
│   ├── urls.py               # Routes
│   ├── admin.py              # Admin config
│   ├── apps.py               # App config
│   └── __init__.py
│
└── [market, orders, agents, billing]/  # Similar structure
```

## Common Issues & Solutions

### Issue: "Connection refused" on database
- Verify DATABASE_URL in .env is correct
- For PostgreSQL: Check postgres service is running
- For SQLite: Check database file is writable
- Test connection: `python manage.py shell`

### Issue: "No such table" errors after migration
- Run: `python manage.py migrate --run-syncdb`
- Check migration files in app directories

### Issue: Images not uploading
- Ensure `media/` directory exists and is writable
- Check file permissions: `chmod 755 media/`

### Issue: Port 8000 already in use
- Use different port: `python manage.py runserver 0.0.0.0:8001`
- Or kill process: `lsof -i :8000` then `kill -9 <PID>`

## Next Steps

1. **Explore the API**: Use Postman or curl to test endpoints
2. **Set up Frontend**: Create a React/Vue/Angular frontend
3. **Configure Production**: Follow deployment guide in README.md
4. **Add Tests**: Write unit and integration tests
5. **Customize Models**: Add additional fields as needed

## Useful Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Supabase Documentation: https://supabase.io/docs

## Support

Check the full README.md for:
- Detailed API documentation
- User role permissions
- Production deployment guide
- Testing strategies
