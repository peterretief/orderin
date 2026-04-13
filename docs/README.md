# Documentation

Complete documentation for the Order In application.

## Quick Navigation

### 🚀 Getting Started
- **[Installation Guide](INSTALLATION.md)** - Complete setup instructions for developers
- **[Quick Start](INSTALLATION.md#step-by-step-installation)** - Get up and running in 5 minutes

### 📖 User Documentation
- **[User Guides](USER_GUIDES.md)** - Complete guides for each user type:
  - [Subscriber Guide](USER_GUIDES.md#subscriber-guide)
  - [Market Agent Guide](USER_GUIDES.md#market-agent-guide)
  - [Delivery Person Guide](USER_GUIDES.md#delivery-person-guide)
  - [Administrator Guide](USER_GUIDES.md#administrator-guide)

### 🔧 Developer Documentation
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference with examples
- **[Development Guidelines](DEVELOPMENT.md)** - Coding standards, testing, and best practices

### 🆘 Troubleshooting
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common issues

---

## Documentation Structure

```
docs/
├── README.md                    # This file
├── INSTALLATION.md              # Setup and installation guide
├── USER_GUIDES.md               # User guides for all user types
├── API_DOCUMENTATION.md         # API endpoints and usage
├── DEVELOPMENT.md               # Developer guidelines and best practices
├── TROUBLESHOOTING.md           # Common issues and solutions
└── images/                      # Screenshots and diagrams (optional)
    ├── login.png
    ├── dashboard.png
    └── profile-edit.png
```

---

## For Different Audiences

### 👤 I'm a User
1. Start with [User Guides](USER_GUIDES.md)
2. Find your user type (Subscriber, Market Agent, etc.)
3. Follow the step-by-step instructions
4. Check [Troubleshooting](TROUBLESHOOTING.md) if you have issues

### 👨‍💻 I'm a Developer
1. Start with [Installation Guide](INSTALLATION.md)
2. Set up your development environment
3. Read [Development Guidelines](DEVELOPMENT.md)
4. Review [API Documentation](API_DOCUMENTATION.md)
5. Check [Troubleshooting](TROUBLESHOOTING.md) if stuck

### 🛠️ I'm Setting Up the Server
1. Follow [Installation Guide](INSTALLATION.md)
2. Configure environment variables
3. Run migrations
4. Create admin account
5. Test the application

### 🚨 I Have a Problem
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search for your error message
3. Follow the suggested solutions
4. If not found, open an issue on GitHub

---

## Key Features Documented

✅ **User Profile Management**
- Edit personal information
- Add contact details
- Update delivery addresses
- Store banking information
- (Market agents) Manage business details

✅ **Address Validation**
- Real-time address geocoding
- Distance calculations
- Delivery cost estimation

✅ **Multi-User System**
- Subscribers (customers)
- Market agents (vendors)
- Delivery persons
- Administrators (system management)

✅ **Order Management**
- Browse marketplace
- Place orders
- Track delivery
- View order history

✅ **Billing System**
- Prepaid account balance
- Multiple payment methods
- Transaction history
- Payout processing

---

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **APIs**: Django REST Framework
- **Geocoding**: geopy (Nominatim)
- **Authentication**: Django Auth + Tokens

---

## Quick Reference

### Common Commands

```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# Database
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create migration files
python manage.py shell                # Python shell

# Testing
python manage.py test                 # Run all tests
python manage.py test users           # Run app tests
coverage report                       # Coverage report

# Admin
python manage.py createsuperuser      # Create admin user
python manage.py changepassword user  # Change password

# Static files
python manage.py collectstatic        # Collect for production
```

### Key URLs (Development)

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Home page |
| http://localhost:8000/login | Login page |
| http://localhost:8000/profile | Edit profile |
| http://localhost:8000/dashboard | User dashboard |
| http://localhost:8000/admin | Admin panel |
| http://localhost:8000/api | API endpoints |

---

## File Structure

```
orderin/
├── config/                 # Django configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
│
├── users/                 # User management (login, profile)
├── market/                # Product marketplace
├── orders/                # Order management
├── agents/                # Service agents
├── billing/               # Billing & balance
├── delivery/              # Delivery management
├── dashboards/            # User dashboards
│
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── media/                 # User uploads
├── docs/                  # Documentation (this folder)
│
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
└── README.md              # Main README
```

---

## Contributing

To improve documentation:

1. Make changes to relevant `.md` file
2. Test links and code examples
3. Submit Pull Request with changes
4. Include description of improvements

---

## Support & Contact

- **Issues**: Open issue on GitHub
- **Email**: support@orderin.local
- **Documentation**: See related `.md` files

---

## Version Information

- **Version**: 1.0.0-beta
- **Last Updated**: April 2026
- **Python**: 3.8+
- **Django**: 4.2+

---

## License

This documentation is part of the Order In project and is licensed under the MIT License.
