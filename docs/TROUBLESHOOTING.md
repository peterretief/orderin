# Troubleshooting Guide

Solutions for common issues.

## Setup & Installation Issues

### Issue: "No module named 'django'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'django'
```

**Solutions:**
1. Check virtual environment is activated:
   ```bash
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. Reinstall dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Verify installation:
   ```bash
   pip list | grep Django
   ```

---

### Issue: "django.core.exceptions.ImproperlyConfigured"

**Symptoms:**
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```

**Causes:**
- Missing `.env` file
- `.env` not properly configured
- DJANGO_SECRET_KEY not set

**Solutions:**
1. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Generate SECRET_KEY:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. Add to `.env`:
   ```
   DJANGO_SECRET_KEY=your-generated-key-here
   ```

---

### Issue: "No such table" error

**Symptoms:**
```
django.db.utils.OperationalError: no such table: users_customuser
```

**Causes:**
- Migrations not run
- Wrong database

**Solutions:**
1. Run migrations:
   ```bash
   python manage.py migrate
   ```

2. Verify migrations:
   ```bash
   python manage.py showmigrations
   ```

3. Reset database (development only):
   ```bash
   rm db.sqlite3
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## Runtime Issues

### Issue: Server won't start

**Symptoms:**
```
Address already in use
```

**Solutions:**
1. Use different port:
   ```bash
   python manage.py runserver 8001
   ```

2. Kill process using port 8000:
   ```bash
   # Linux/macOS
   sudo lsof -i :8000
   kill -9 <PID>
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

3. Wait a few seconds and try again

---

### Issue: Static files not loading

**Symptoms:**
- CSS/JS files return 404
- Images not displaying

**Causes:**
- Static files not collected
- STATIC_URL configured incorrectly

**Solutions:**
1. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. Check DEBUG setting:
   ```python
   # In development (settings.py)
   DEBUG = True
   ```

3. Verify STATIC_ROOT and STATIC_URL in settings.py:
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   ```

---

### Issue: Template not found

**Symptoms:**
```
TemplateDoesNotExist: dashboard.html
```

**Causes:**
- Template file doesn't exist
- Template directory not configured
- Wrong path

**Solutions:**
1. Verify template exists:
   ```bash
   ls templates/dashboards/dashboard.html
   ```

2. Check TEMPLATES configuration in settings.py:
   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [os.path.join(BASE_DIR, 'templates')],
           'APP_DIRS': True,
           ...
       }
   ]
   ```

3. Restart server after configuration changes

---

## Profile & Address Issues

### Issue: Address validation always fails

**Symptoms:**
- "Address not found" error for valid addresses
- Distance calculation shows wrong results

**Causes:**
- Address too generic (e.g., "Suburb" instead of "Observatory, Western Cape")
- Network connectivity issues
- Nominatim service down

**Solutions:**
1. Use more specific address:
   ```
   ✅ Good: "300 Main Street, Observatory, Western Cape, South Africa"
   ❌ Bad: "300 Main Street, Suburb"
   ```

2. Include city and province:
   ```
   ✅ Good: "Cape Town, Western Cape"
   ❌ Bad: "Cape Town"
   ```

3. Test address manually:
   ```python
   from delivery.distance import DeliveryDistanceAndCost
   
   validator = DeliveryDistanceAndCost()
   result = validator.geocode_address("Cape Town, Western Cape")
   print(result)
   ```

---

### Issue: Banking fields not visible on profile

**Symptoms:**
- Banking Information section missing from edit profile form

**Causes:**
- Migrations not applied
- Template not updated
- Cache issue

**Solutions:**
1. Run migrations:
   ```bash
   python manage.py migrate users
   ```

2. Clear cache:
   ```bash
   python manage.py clear_cache
   ```

3. Hard refresh browser:
   ```
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (macOS)
   ```

---

## Database Issues

### Issue: Cannot connect to database

**Symptoms:**
```
could not connect to server: Connection refused
```

**Causes:**
- Database server not running
- Wrong connection string
- Wrong credentials

**Solutions:**
1. Check database is running:
   ```bash
   # For PostgreSQL
   pg_isready -h localhost -p 5432
   ```

2. Verify connection string in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/orderin
   ```

3. Test connection:
   ```bash
   python manage.py dbshell
   ```

---

### Issue: Migration conflicts

**Symptoms:**
```
Conflict detected: both migrations alter column X
```

**Causes:**
- Multiple migrations modifying same field
- Manual SQL changes

**Solutions:**
1. Review conflicting migrations:
   ```bash
   ls users/migrations/
   ```

2. Reorder migrations if needed

3. In critical cases, reset and remigrate:
   ```bash
   python manage.py migrate users --fake-initial
   ```

---

## Authentication Issues

### Issue: Cannot login

**Symptoms:**
- "Invalid username or password"
- Login page doesn't submit

**Causes:**
- Wrong credentials
- User inactive
- Session expired

**Solutions:**
1. Reset password using admin:
   ```bash
   python manage.py changepassword username
   ```

2. Check user is active:
   ```bash
   python manage.py shell
   # Then run:
   from users.models import CustomUser
   user = CustomUser.objects.get(username='username')
   print(user.is_active)
   ```

3. Clear browser cookies and try again

---

### Issue: Permission denied accessing admin

**Symptoms:**
```
PermissionDenied: You don't have permission to access this
```

**Causes:**
- User is not superuser
- User is inactive

**Solutions:**
1. Make user superuser:
   ```bash
   python manage.py shell
   # Then run:
   from users.models import CustomUser
   user = CustomUser.objects.get(username='username')
   user.is_staff = True
   user.is_superuser = True
   user.save()
   ```

2. Activate user:
   ```bash
   python manage.py shell
   # Then run:
   user.is_active = True
   user.save()
   ```

---

## API Issues

### Issue: API returns 401 Unauthorized

**Symptoms:**
```json
{"detail": "Authentication credentials were not provided."}
```

**Causes:**
- Missing authentication token
- Token expired
- Invalid token

**Solutions:**
1. Get authentication token:
   ```bash
   curl -X POST http://localhost:8000/api/users/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'
   ```

2. Include token in requests:
   ```bash
   curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/users/profile/
   ```

---

### Issue: API returns 400 Bad Request

**Symptoms:**
```json
{"error": "Invalid request parameters"}
```

**Causes:**
- Missing required fields
- Invalid data type
- Validation error

**Solutions:**
1. Check request body format
2. Verify all required fields are present
3. Check data types match specification
4. Look at error details for specific issues

---

## Performance Issues

### Issue: Site is slow

**Symptoms:**
- Pages load slowly
- API responses are delayed

**Causes:**
- Database queries slow
- N+1 query problem
- Large data transfers

**Solutions:**
1. Check database queries:
   ```bash
   python manage.py shell
   from django.db import connection
   from django.test.utils import CaptureQueriesContext
   
   with CaptureQueriesContext(connection) as context:
       # Run code here
       pass
   
   print(f"{len(context.captured_queries)} queries")
   ```

2. Optimize with select_related/prefetch_related:
   ```python
   # Instead of orders = Order.objects.all()
   orders = Order.objects.select_related('customer', 'market_agent')
   ```

3. Add database indexes:
   ```python
   class Order(models.Model):
       created_at = models.DateTimeField(auto_now_add=True, db_index=True)
   ```

---

## Email Not Sending

### Issue: Emails not received

**Symptoms:**
- No password reset emails
- No order confirmation emails

**Causes:**
- Email not configured
- SMTP credentials wrong
- Email going to spam

**Solutions:**
1. Test email configuration:
   ```bash
   python manage.py shell
   from django.core.mail import send_mail
   
   send_mail(
       'Test Subject',
       'Test message',
       'from@example.com',
       ['to@example.com'],
   )
   ```

2. Check email settings in `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-password
   ```

3. Check spam folder

---

## Getting Help

If your issue isn't solved:

1. **Check the logs**:
   ```bash
   tail -f logs/django.log
   ```

2. **Search GitHub Issues**:
   - Look for similar issues
   - Check closed issues for solutions

3. **Ask for help**:
   - Describe the issue clearly
   - Include error messages
   - Share relevant code
   - Mention your setup (OS, Python version, etc.)

4. **Enable debug mode** (development only):
   ```python
   DEBUG = True
   ```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No such table` | Migrations not run | `python manage.py migrate` |
| `Address already in use` | Port occupied | Use different port or kill process |
| `TemplateDoesNotExist` | Template file missing | Check template path and file exists |
| `ModuleNotFoundError` | Package not installed | Run `pip install -r requirements.txt` |
| `PermissionDenied` | User lacks permission | Check user type and permissions |
| `ValidationError` | Invalid form data | Check form input and validation rules |
| `IntegrityError` | Database constraint violated | Check unique fields and foreign keys |
| `ObjectDoesNotExist` | Record not found | Verify object ID and query conditions |
