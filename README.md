# Order In - Django Subscription-Based Market Application

A comprehensive Django application for managing a subscription-based online marketplace with service agents (delivery and catering), billing, user profile management, and user balance management.

> **Status**: Active Development | **Python**: 3.8+ | **Django**: 4.2+ | **Database**: SQLite/PostgreSQL

## 🎯 Features

### User Types
- **Administrator**: Manage the platform, billing plans, and subscriber billing
- **Subscriber**: Order from marketplace with prepaid balance system
- **Market Agent**: Manage products, inventory, and market information
- **Service Agents**: 
  - **Delivery Person**: Transport services with geographic coverage
  - **Caterer**: Recipe creation and catering services

### Core Features
- ✅ Multi-role user authentication and authorization
- ✅ **Comprehensive Profile Management** - Edit name, contact, address, banking, and business info
- ✅ **Banking Information Storage** - Bank name, account number, account type, branch code
- ✅ **Address Validation** - Real-time address geocoding using Nominatim
- ✅ **Distance Calculation** - Automatic delivery cost calculation based on address
- ✅ Online marketplace for ingredients and produce
- ✅ Order management with status tracking
- ✅ Balance-based payment system (prepaid)
- ✅ Optional service agents per order
- ✅ Product inventory management
- ✅ Transaction history and audit trails
- ✅ Responsive dashboard for all user types

## 📋 Project Structure

```
orderin/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
│
├── users/                 # User management & profiles
│   ├── models.py          # CustomUser with profile fields
│   ├── auth_views.py      # Authentication & profile editing
│   ├── views.py           # User endpoints
│   ├── serializers.py     # Data serializers
│   └── urls.py            # User routes
│
├── market/                # Product marketplace
│   ├── models.py          # Product, ProductCategory
│   ├── views.py           # Product endpoints
│   ├── shop_views.py      # Shop interface
│   ├── serializers.py     # Data serializers
│   └── urls.py            # Market routes
│
├── orders/                # Order management
│   ├── models.py          # Order, OrderItem, OrderServiceAgent
│   ├── views.py           # Order endpoints and logic
│   ├── serializers.py     # Data serializers
│   └── urls.py            # Order routes
│
├── agents/                # Service agents
│   ├── models.py          # Service pricing and availability
│   ├── views.py           # Agent endpoints
│   ├── serializers.py     # Data serializers
│   └── urls.py            # Agent routes
│
├── billing/               # Billing, balance & payments
│   ├── models.py          # Balance, Transactions, Plans
│   ├── views.py           # Billing endpoints
│   ├── business_account.py# Business account handling
│   ├── serializers.py     # Data serializers
│   └── urls.py            # Billing routes
│
├── dashboards/            # User dashboards
│   ├── models.py          # Dashboard configurations
│   ├── views.py           # Dashboard views
│   └── urls.py            # Dashboard routes
│
├── delivery/              # Delivery management
│   ├── distance.py        # Distance & cost calculation
│   ├── views.py           # Delivery endpoints
│   └── urls.py            # Delivery routes
│
├── templates/             # HTML templates
│   ├── auth/              # Authentication templates
│   ├── dashboards/        # Dashboard templates
│   ├── shop/              # Shop templates
│   └── billing/           # Billing templates
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd orderin

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

Access the app at: **http://localhost:8000**

## 👤 User Profiles

All users can edit their comprehensive profile at `/profile/` with the following sections:

### Universal Profile Fields (All Users)
- **Personal**: First name, last name
- **Contact**: Email (required), phone number
- **Location**: Street address, city, state/province, postal code
- **Banking**: Bank name, account holder, account number, branch code, account type

### Market Agent Fields
- **Business**: Market/shop name, business description

These fields are used for:
- 📍 **Address Validation** - Real-time geocoding with Nominatim
- 💰 **Cost Calculation** - Automatic delivery distance & cost calculation
- 🏦 **Payouts** - Secure banking information for payments
- 🏪 **Business Profile** - Marketing and customer discovery

## 🔐 Authentication & Authorization

### User Types & Permissions

**Subscriber Role**
- Create and manage orders
- View order history and status
- Manage account balance
- Edit profile and address
- Track deliveries

**Market Agent Role**
- Upload and manage products
- Manage inventory and pricing
- Edit store/market information
- View sales and orders
- Manage banking information

**Delivery Person Role**
- View assigned deliveries
- Update delivery status
- Manage coverage area
- Edit profile and banking info

**Caterer Role**
- Create and manage recipes
- Set pricing
- Manage availability
- Edit profile information

**Administrator Role**
- Access Django admin panel
- Manage all users and accounts
- Create billing plans
- View all orders and transactions
- Access system logs and reports

## 🌐 API Endpoints

### Profile & Authentication `/users/`
```
POST   /login/                    - User login
POST   /logout/                   - User logout
GET/POST /profile/                - View/edit user profile
```

### Market & Products `/market/`
```
GET    /products/                 - List all products
POST   /products/                 - Create product (agents)
GET    /products/{id}/            - Product details
PUT    /products/{id}/            - Update product
GET    /categories/               - List categories
```

### Orders `/orders/`
```
POST   /                          - Create order
GET    /                          - List user orders
GET    /{id}/                     - Order details
PUT    /{id}/status/              - Update status (admin)
```

### Billing & Balance `/billing/`
```
GET    /balance/                  - User balance
POST   /balance/add/              - Add funds
GET    /transactions/             - Transaction history
GET    /plans/                    - Available plans
```

### Delivery `/delivery/`
```
POST   /calculate-cost/           - Calculate delivery cost
POST   /validate-address/         - Validate address geocoding
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 4.2+ |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5, jQuery |
| APIs | Django REST Framework |
| Geocoding | geopy (Nominatim) |
| Authentication | Django Auth + Tokens |

## 📦 Dependencies

See `requirements.txt` for complete list. Key packages:
- Django 4.2+
- djangorestframework
- django-cors-headers
- geopy (for address geocoding)
- Pillow (image handling)

## 📝 Environment Variables

Create `.env` file with:
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/orderin
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test market
python manage.py test orders
```

## 📱 Key Features in Detail

### Profile Editing (`/profile/`)
- Edit name, email, phone for all users
- Update delivery address with real-time validation
- Store banking information securely
- Market agents can edit business name and description
- All changes saved to database immediately

### Address Validation
- Real-time address geocoding using Nominatim
- Automatic distance calculation to service areas
- Visual status indicators (valid/invalid addresses)
- Prevents invalid delivery addresses at checkout

### Banking Information
- Store bank account details securely
- Account types: Savings, Cheque, Business
- Required for payout processing
- Optional fields: branch code, international info

### Distance & Delivery Costs
- Automatic calculation based on store and customer addresses
- Geographic validation using geopy
- Real-time cost estimation
- Distance-based pricing support

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push to branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions, please open an issue on GitHub or contact the development team.

## 📞 Contact

- **Email**: support@orderin.local
- **Issues**: GitHub Issues
- **Documentation**: See docs folder

---

**Last Updated**: April 2026 | **Version**: 1.0.0-beta
- Cannot place orders

### Service Agents (Caterer/Delivery)
- Set their service pricing
- Manage availability slots
- View assigned orders
- Update service status

## Workflow Examples

### 1. Subscriber Ordering

1. Subscriber adds funds: `POST /api/billing/balance/add_funds/` (amount: 500)
2. Subscriber views products: `GET /api/market/products/`
3. Subscriber creates order: `POST /api/orders/create_order/`
   ```json
   {
     "items": [
       {"product_id": 1, "quantity": 2},
       {"product_id": 3, "quantity": 1}
     ],
     "service_agents": [
       {"service_agent_id": 2, "price": 50},
       {"service_agent_id": 5, "price": 75}
     ],
     "notes": "Please deliver by 5 PM"
   }
   ```
4. Admin marks order as delivered: `PUT /api/orders/{id}/update_status/`
5. Admin bills order: `GET /api/orders/{id}/bill_order/`

### 2. Market Agent Managing Products

1. Market agent creates product: `POST /api/market/products/`
   ```json
   {
     "category": 1,
     "name": "Fresh Tomatoes",
     "sku": "TOMATO-001",
     "price": "50.00",
     "quantity_available": 100,
     "unit": "kg",
     "image": "file.jpg"
   }
   ```
2. Updates stock: `PUT /api/market/products/{id}/update_availability/`

### 3. Service Agent Setting Pricing

1. Caterer sets pricing: `PUT /api/agents/pricing/update_my_pricing/`
   ```json
   {
     "base_price": "200.00",
     "price_per_item": "10.00"
   }
   ```
2. Sets availability: `POST /api/agents/availability/add_availability/`

## Database Models

### Core Models

**CustomUser**
- Extends Django's AbstractUser
- Fields: username, email, password, user_type, phone, address, city, state, zip_code
- User types: admin, subscriber, market_agent, caterer, delivery_person

**ServiceAgent**
- Linked to CustomUser
- Fields: service_type, is_active, rating, total_services, specialty, vehicle_type

**MarketAgent**
- Linked to CustomUser
- Fields: is_active

**Product**
- Belongs to MarketAgent
- Fields: name, description, sku, price, quantity_available, unit, image, category

**Order**
- Belongs to Subscriber (CustomUser)
- Statuses: pending, confirmed, being_prepared, ready_for_delivery, in_transit, delivered, cancelled
- Fields: total_price, service_fee, total_amount, status, notes

**OrderItem**
- Belongs to Order and Product
- Fields: quantity, unit_price, total_price

**OrderServiceAgent**
- Links Order to ServiceAgent
- Fields: service_type, price, notes

**UserBalance**
- One-to-one with CustomUser
- Fields: balance (decimal), created_at, updated_at

**BillingTransaction**
- Belongs to CustomUser and Order
- Types: credit, debit
- Fields: amount, type, description, balance_after

## Testing the API

### Using curl

```bash
# Register subscriber
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "user_type": "subscriber"
  }'

# Login
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "securepass123"}'

# Add funds
curl -X POST http://localhost:8000/api/billing/balance/add_funds/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=your_session_id" \
  -d '{"amount": "500"}'
```

### Using Postman

1. Import the API endpoints into Postman
2. Set up authentication with Session cookies
3. Create requests for each endpoint
4. Use environment variables for base URL and session IDs

## Production Deployment

1. **Update settings.py**:
   - Set `DEBUG = False`
   - Add your domain to `ALLOWED_HOSTS`
   - Generate a strong `DJANGO_SECRET_KEY`
   - Configure allowed CORS origins

2. **Configure Static/Media Files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Use Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn config.wsgi
   ```

4. **Set up Nginx** as reverse proxy

5. **Enable HTTPS** with SSL certificates

6. **Database Backups**: Set up regular Supabase backups

## Troubleshooting

### Database Connection Errors
- Verify Supabase is running on 192.168.0.102:8000
- Check DB_PASSWORD in .env file
- Ensure PostgreSQL is accessible

### Migration Errors
- Run: `python manage.py migrate --run-syncdb`
- Check for circular imports in models

### Permission Denied Errors
- Ensure user has correct user_type
- Check staff/admin status for admin endpoints

## Contributing

1. Create feature branches
2. Write tests for new features
3. Submit pull requests

## License

MIT License - Feel free to use this project

## Support

For issues or questions, contact the development team or check the documentation.
