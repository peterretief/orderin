# API Documentation

Complete API reference for Order In application.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Most endpoints require authentication. Include the token in the header:

```
Authorization: Token YOUR_AUTH_TOKEN
```

## User Profile Endpoints

### Edit Profile
- **URL**: `/profile/` (or `GET` for form, `POST` for submission)
- **Method**: `GET`, `POST`
- **Auth Required**: Yes
- **Description**: View and edit user profile including contact, address, and banking info

**POST Parameters:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+27 123 456 7890",
  "address": "123 Main Street",
  "city": "Cape Town",
  "state": "Western Cape",
  "zip_code": "8000",
  "bank_name": "Standard Bank",
  "bank_account_holder_name": "John Doe",
  "bank_account_number": "123456789",
  "bank_branch_code": "051001",
  "bank_account_type": "checking",
  "shop_name": "Fresh Market",           // Market agents only
  "shop_description": "Organic produce"  // Market agents only
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Your profile has been updated successfully!"
}
```

## Market Product Endpoints

### List All Products
- **URL**: `/market/products/`
- **Method**: `GET`
- **Auth Required**: No
- **Description**: Get all available products

**Response:**
```json
[
  {
    "id": 1,
    "name": "Organic Tomatoes",
    "price": 45.50,
    "category": "Vegetables",
    "shop_name": "Fresh Produce Market",
    "available_quantity": 100,
    "image": "url..."
  },
  ...
]
```

### Create Product
- **URL**: `/market/products/`
- **Method**: `POST`
- **Auth Required**: Yes (Market Agent only)
- **Description**: Create new product

**POST Parameters:**
```json
{
  "name": "Organic Tomatoes",
  "description": "Fresh, ripe tomatoes",
  "price": 45.50,
  "category": "Vegetables",
  "available_quantity": 100,
  "sku": "ORG-TOM-001",
  "image": "file_upload"
}
```

### Update Product
- **URL**: `/market/products/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Owner only)
- **Description**: Update product details

### Delete Product
- **URL**: `/market/products/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Owner only)
- **Description**: Delete a product

## Order Endpoints

### Create Order
- **URL**: `/orders/`
- **Method**: `POST`
- **Auth Required**: Yes (Subscribers)
- **Description**: Create new order

**POST Parameters:**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ],
  "delivery_address": "456 Oak Street, Cape Town",
  "delivery_type": "delivery",  // or "pickup"
  "service_agents": {
    "delivery_person": 5,  // Optional
    "caterer": null
  }
}
```

**Response (201 Created):**
```json
{
  "id": 45,
  "order_number": "ORD-20260413-001",
  "total_amount": 150.00,
  "status": "pending",
  "created_at": "2026-04-13T10:30:00Z"
}
```

### List Orders
- **URL**: `/orders/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Get user's orders

**Query Parameters:**
```
?status=pending          # Filter by status
?page=1                  # Pagination
?limit=10                # Items per page
```

### Order Details
- **URL**: `/orders/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Get specific order details

### Update Order Status
- **URL**: `/orders/{id}/status/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)

**POST Parameters:**
```json
{
  "status": "confirmed"  // pending, confirmed, processing, delivered, cancelled
}
```

## Billing & Balance Endpoints

### Get User Balance
- **URL**: `/billing/balance/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Check current account balance

**Response:**
```json
{
  "balance": 5000.00,
  "currency": "ZAR",
  "last_updated": "2026-04-13T10:30:00Z"
}
```

### Add Funds
- **URL**: `/billing/balance/add-funds/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Add funds to account

**POST Parameters:**
```json
{
  "amount": 500.00,
  "payment_method": "card"  // or "bank_transfer"
}
```

### Transaction History
- **URL**: `/billing/transactions/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: View transaction history

**Query Parameters:**
```
?start_date=2026-04-01
?end_date=2026-04-13
?type=debit              # credit, debit, all
?page=1
```

### Billing Plans
- **URL**: `/billing/plans/`
- **Method**: `GET`
- **Auth Required**: No
- **Description**: Get available billing plans

## Delivery Endpoints

### Calculate Delivery Cost
- **URL**: `/delivery/calculate-cost/`
- **Method**: `POST`
- **Auth Required**: No
- **Description**: Calculate delivery cost based on distance

**POST Parameters:**
```json
{
  "from_address": "123 Market Street, Cape Town",
  "to_address": "456 Customer Road, Cape Town"
}
```

**Response:**
```json
{
  "distance_km": 5.2,
  "estimated_cost": 50.00,
  "currency": "ZAR"
}
```

### Validate Address
- **URL**: `/delivery/validate-address/`
- **Method**: `POST`
- **Auth Required**: No
- **Description**: Validate and geocode address

**POST Parameters:**
```json
{
  "address": "Cape Town, Western Cape, South Africa"
}
```

**Response:**
```json
{
  "valid": true,
  "latitude": -33.9249,
  "longitude": 18.4241,
  "formatted_address": "Cape Town, Western Cape, South Africa"
}
```

Or if invalid:
```json
{
  "valid": false,
  "error": "Address not found or too generic"
}
```

## Service Agent Endpoints

### Get My Pricing
- **URL**: `/agents/pricing/my-pricing/`
- **Method**: `GET`
- **Auth Required**: Yes (Service Agents)
- **Description**: Get your service pricing

### Update Pricing
- **URL**: `/agents/pricing/update-pricing/`
- **Method**: `PUT`
- **Auth Required**: Yes (Service Agents)

**POST Parameters:**
```json
{
  "base_price": 150.00,
  "per_km_rate": 5.50,
  "minimum_charge": 50.00
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred",
  "message": "Error details..."
}
```

## Rate Limiting

Rate limits are applied to prevent abuse:
- **General endpoints**: 100 requests per hour
- **Authentication**: 5 failed attempts per 15 minutes
- **File uploads**: 10 MB maximum file size

## Pagination

List endpoints support pagination with these parameters:
```
?page=1          # Page number (1-indexed)
?limit=20        # Items per page (default: 20, max: 100)
```

Response includes pagination info:
```json
{
  "count": 150,
  "next": "http://api.example.com/products/?page=2",
  "previous": null,
  "results": [...]
}
```

## Webhooks (Coming Soon)

Webhooks will be available for order status updates, payment confirmations, and other events.
