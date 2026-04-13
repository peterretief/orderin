# Order In - Database Schema & Relationships

## Entity Relationship Diagram (Text Format)

```
┌─────────────────────────────────────────────────────────────────────┐
│                            CustomUser                               │
├─────────────────────────────────────────────────────────────────────┤
│ • id (PK)                                                           │
│ • username, email, password                                         │
│ • first_name, last_name                                             │
│ • phone, address, city, state, zip_code                             │
│ • user_type [admin, subscriber, market_agent, caterer, delivery]   │
│ • is_verified, is_active, is_staff, is_superuser                   │
│ • shop_name, shop_description, shop_logo (for market agents)       │
│ • service_name, service_description, service_image (for agents)    │
│ • date_joined, created_at, updated_at                              │
└─────────────────────────────────────────────────────────────────────┘
    │                         │                          │
    │ (1:1)                   │ (1:1)                    │ (1:1)
    ├─────────────────├──────────────────┼──────────────┤
    │                 │                  │              │
    ▼                 ▼                  ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│UserBalance   │ │ServiceAgent   │ │MarketAgent   │ │BillingTransaction│
│──────────────│ │──────────────│ │──────────────│ │──────────────────│
│• user (FK)   │ │• user (FK)   │ │• user (FK)   │ │• user (FK)       │
│• balance     │ │• service_type│ │• is_active   │ │• amount          │
│• created_at  │ │• is_active   │ │• created_at  │ │• type [+/-]      │
│• updated_at  │ │• rating      │ │• updated_at  │ │• balance_after   │
│              │ │• specialty   │ │              │ │• description     │
│              │ │• vehicle_type│ │              │ │• order_id (FK)   │
│              │ │• created_at  │ │              │ │• created_at      │
└──────────────┘ │• updated_at  │ └──────────────┘ └──────────────────┘
                 └──────────────┘
                      │
                      │ (1:1)
                      ▼
                ┌──────────────────┐
                │  ServicePrice    │
                ├──────────────────┤
                │• service_agent   │
                │• base_price      │
                │• price_per_item  │
                │• price_per_km    │
                │• created_at      │
                │• updated_at      │
                └──────────────────┘

                      │
                      │ (1:N)
                      ▼
                ┌──────────────────────┐
                │ServiceAvailability   │
                ├──────────────────────┤
                │• service_agent (FK)  │
                │• day_of_week         │
                │• start_time          │
                │• end_time            │
                │• is_available        │
                │• created_at          │
                │• updated_at          │
                └──────────────────────┘
```

## Market Entities

```
┌──────────────────────────────────────────┐
│         ProductCategory                  │
├──────────────────────────────────────────┤
│• id (PK)                                 │
│• name                                    │
│• description                             │
└──────────────────────────────────────────┘
          │
          │ (1:N)
          ▼
┌──────────────────────────────────────────┐
│           Product                        │
├──────────────────────────────────────────┤
│• id (PK)                                 │
│• market_agent_id (FK → MarketAgent)      │
│• category_id (FK → ProductCategory)      │
│• name, description                       │
│• sku (unique per agent)                  │
│• price                                   │
│• quantity_available                      │
│• unit (kg, piece, liter, etc)           │
│• image                                   │
│• is_available                            │
│• created_at, updated_at                  │
└──────────────────────────────────────────┘
```

## Order Entities

```
┌──────────────────────────────────────────────────┐
│                   Order                          │
├──────────────────────────────────────────────────┤
│• id (PK)                                         │
│• subscriber_id (FK → CustomUser)                 │
│• status [pending, confirmed, being_prepared...] │
│• total_price                                     │
│• service_fee                                     │
│• total_amount                                    │
│• notes                                           │
│• created_at, updated_at, delivered_at           │
└──────────────────────────────────────────────────┘
    │                              │
    │ (1:N)                        │ (1:N)
    ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────────┐
│       OrderItem              │ │  OrderServiceAgent             │
├──────────────────────────────┤ ├────────────────────────────────┤
│• id (PK)                     │ │• id (PK)                       │
│• order_id (FK)               │ │• order_id (FK)                 │
│• product_id (FK → Product)   │ │• service_agent_id (FK)         │
│• quantity                    │ │• service_type [catering, ...]  │
│• unit_price                  │ │• price                         │
│• total_price                 │ │• notes                         │
│• created_at                  │ │• created_at                    │
│                              │ │• Unique(order, service_agent)  │
└──────────────────────────────┘ └────────────────────────────────┘
```

## Billing Entities

```
┌──────────────────────────────────────────┐
│        BillingPlan                       │
├──────────────────────────────────────────┤
│• id (PK)                                 │
│• name                                    │
│• description                             │
│• plan_type [monthly, per_order]          │
│• amount                                  │
│• is_active                               │
│• created_at, updated_at                  │
└──────────────────────────────────────────┘
          │
          │ (1:N)
          ▼
┌──────────────────────────────────────────┐
│        AdminBilling                      │
├──────────────────────────────────────────┤
│• id (PK)                                 │
│• subscriber_id (FK → CustomUser)         │
│• billing_plan_id (FK)                    │
│• amount                                  │
│• status [pending, paid, overdue]         │
│• billing_date                            │
│• due_date                                │
│• paid_date                               │
│• created_at, updated_at                  │
└──────────────────────────────────────────┘
```

## Key Relationships

### User Type Workflows

#### Subscriber
```
CustomUser (user_type='subscriber')
    ↓
UserBalance (one-to-one)
    ↓
Order (many)
    ├─→ OrderItem (many per order)
    │    └─→ Product
    │
    └─→ OrderServiceAgent (optional, many per order)
        └─→ ServiceAgent

+ AdminBilling (many) - for subscription charges
+ BillingTransaction (many) - transaction history
```

#### Market Agent
```
CustomUser (user_type='market_agent')
    ↓
MarketAgent (one-to-one)
    ↓
Product (many)
    └─→ ProductCategory
        └─→ OrderItem (many)
            └─→ Order
```

#### Service Agent (Caterer/Delivery)
```
CustomUser (user_type='caterer' or 'delivery_person')
    ↓
ServiceAgent (one-to-one)
    ├─→ ServicePrice (one-to-one)
    │
    └─→ ServiceAvailability (many - time slots)

    └─→ OrderServiceAgent (many)
        └─→ Order
```

## Data Validation Rules

### CustomUser Model
- `username`: Unique, max 150 chars
- `email`: Unique
- `user_type`: Must be one of valid choices
- `phone`: Optional, max 20 chars
- `password`: Min 8 chars (enforced by Django)

### Product Model
- `price`: Decimal, max_digits=10, decimal_places=2 (0.00 to 9999999.99)
- `quantity_available`: Non-negative integer
- `sku`: Unique per market agent
- `unit`: Free text (kg, piece, liter, etc)

### Order Model
- `status`: Must be one of valid choices
- `subscriber` user_type must be 'subscriber'
- Can't create if subscriber.balance <= 0
- `total_amount` = total_price + service_fee

### OrderItem
- `quantity`: > 0
- `unit_price`: >= 0
- `total_price` auto-calculated = quantity × unit_price

### UserBalance
- `balance`: Can be positive or negative (after billing)
- One-to-one relationship with CustomUser

### BillingTransaction
- `type`: 'credit' (add funds) or 'debit' (charge)
- `balance_after`: Recorded state of balance after transaction
- Immutable audit trail

## Database Indexes

```sql
-- Performance optimization indexes
CREATE INDEX idx_order_subscriber ON orders_order(subscriber_id);
CREATE INDEX idx_order_status ON orders_order(status);
CREATE INDEX idx_orderitem_order ON orders_orderitem(order_id);
CREATE INDEX idx_product_market_agent ON market_product(market_agent_id);
CREATE INDEX idx_product_category ON market_product(category_id);
CREATE INDEX idx_product_available ON market_product(is_available);
CREATE INDEX idx_serviceagent_type ON users_serviceagent(service_type);
CREATE INDEX idx_billingtx_user ON billing_billingtransaction(user_id);
CREATE INDEX idx_billingtx_type ON billing_billingtransaction(type);
CREATE INDEX idx_adminbilling_status ON billing_adminbilling(status);
CREATE INDEX idx_adminbilling_date ON billing_adminbilling(billing_date);
```

## SQL Queries For Common Operations

### Get User's Total Orders and Spending
```sql
SELECT 
    u.username,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    b.balance as current_balance
FROM users_customuser u
LEFT JOIN orders_order o ON u.id = o.subscriber_id
LEFT JOIN billing_userbalance b ON u.id = b.user_id
WHERE u.id = ?
GROUP BY u.id, u.username, b.balance;
```

### Get Market Agent's Top Products
```sql
SELECT 
    p.name,
    p.price,
    COUNT(oi.id) as times_ordered,
    SUM(oi.quantity) as total_quantity_sold
FROM market_product p
LEFT JOIN orders_orderitem oi ON p.id = oi.product_id
WHERE p.market_agent_id = ?
GROUP BY p.id, p.name, p.price
ORDER BY COUNT(oi.id) DESC
LIMIT 10;
```

### Get Service Agent's Revenue
```sql
SELECT 
    sa.user_id,
    u.service_name,
    COUNT(osa.id) as total_services,
    SUM(osa.price) as total_revenue,
    AVG(sa.rating) as rating
FROM users_serviceagent sa
LEFT JOIN orders_orderserviceagent osa ON sa.id = osa.service_agent_id
LEFT JOIN users_customuser u ON sa.user_id = u.id
WHERE sa.id = ?
GROUP BY sa.id, sa.user_id, u.service_name;
```

### Find Overdue Bills
```sql
SELECT 
    ab.id,
    u.username,
    ab.amount,
    ab.due_date,
    DATEDIFF(NOW(), ab.due_date) as days_overdue
FROM billing_adminbilling ab
JOIN users_customuser u ON ab.subscriber_id = u.id
WHERE ab.status = 'pending'
AND ab.due_date < NOW()
ORDER BY ab.due_date;
```

## Migrations Strategy

When adding new features:

1. **Create new models** → Run `makemigrations`
2. **Review migrations** in `migrations/` folder
3. **Test migrations** → `migrate --plan`
4. **Apply migrations** → `migrate`
5. **Update admin.py** if needed
6. **Update serializers** in REST API
7. **Update views** with new endpoints

Example:
```bash
python manage.py makemigrations orders
python manage.py migrate orders --plan  # Preview
python manage.py migrate orders         # Apply
```
