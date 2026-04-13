# Business Account Transaction System

## Overview

All money transactions in Order In now flow through a **single, centralized Business Account**. This makes it easy to:

- ✅ Track all money in and out
- ✅ Reconcile accounts quickly
- ✅ Generate financial reports
- ✅ Audit transaction history
- ✅ Prevent data inconsistency

## How It Works

### Transaction Flow

```
SUBSCRIBER
    ↓
    ├─ Deposits Money → Business Account (IN)
    │
    └─ Makes Purchase → Business Account (OUT to Marketplace)
        ↓
        ├─ Market Agent Paid (OUT from Business Account)
        └─ Service Agent Paid (OUT from Business Account)
```

### Business Transaction Types

| Type | Flow | Description |
|------|------|-------------|
| `subscriber_deposit` | ➕ IN | Subscriber adds funds (balance increase) |
| `subscriber_purchase` | ➖ OUT | Subscriber buys products (money goes to sellers) |
| `market_agent_payout` | ➖ OUT | Payment to market agent for products sold |
| `service_agent_payout` | ➖ OUT | Payment to service agent (delivery, etc.) |
| `refund` | ➖ OUT | Refund to subscriber |
| `admin_fee` | ➕ IN | Commission collected by platform |
| `adjustment` | ± | Manual adjustments (corrections, etc.) |

## API Endpoints

### Get Business Account Information
```
GET /api/billing/business-account/main-account/
```
Returns the main business account details and balance.

### Get Business Transaction Summary
```
GET /api/billing/business-transactions/summary/
```
Returns:
- Total account balance
- Count and total for each transaction type
- Total transaction count

### Get Transactions by Type
```
GET /api/billing/business-transactions/by-type/?type=subscriber_deposit
```
Filter transactions by type.

### List All Business Transactions
```
GET /api/billing/business-transactions/
```
Get full list of all transactions (admin only).

## Python Functions

Use these helper functions in your code to record transactions:

### Recording Transactions

```python
from billing.business_account import (
    record_subscriber_deposit,
    record_subscriber_purchase,
    record_market_agent_payout,
    record_service_agent_payout,
    record_refund,
    record_admin_fee,
    record_adjustment,
    get_business_account_balance
)

# Record subscriber deposit
record_subscriber_deposit(
    subscriber=user,
    amount=1000,
    reference_id='STRIPE_CHG_123',
    notes='Deposit via Stripe'
)

# Record subscriber purchase
record_subscriber_purchase(
    subscriber=subscriber,
    amount=150,
    order=order,
    notes='Order #123 purchase'
)

# Record market agent payout
record_market_agent_payout(
    market_agent=agent,
    amount=100,
    order=order,
    notes='Payment for sold products'
)

# Record service agent payout
record_service_agent_payout(
    service_agent=agent,
    amount=50,
    order=order,
    notes='Delivery fee'
)

# Record refund
record_refund(
    subscriber=user,
    amount=150,
    order=order,
    notes='Order cancelled'
)

# Record admin fee (commission)
record_admin_fee(
    amount=15,
    description='Platform commission - 10%',
    order=order
)

# Get current balance
balance = get_business_account_balance()
print(f"Account balance: R {balance}")
```

## Database Schema

### BusinessAccount
```
id              (Integer, Primary Key)
name            (String) - Account name
status          (Choice) - active/inactive
description     (Text) - Account description
total_balance   (Decimal) - Current balance
created_at      (DateTime) - Created timestamp
updated_at      (DateTime) - Last update timestamp
```

### BusinessTransaction
```
id                  (Integer, Primary Key)
business_account_id (Foreign Key) - Which account
subscriber_id       (Foreign Key) - Which user (if applicable)
market_agent_id     (Foreign Key) - Which market agent (if applicable)
service_agent_id    (Foreign Key) - Which service agent (if applicable)
order_id            (Foreign Key) - Which order (if applicable)
type                (Choice) - Transaction type
amount              (Decimal) - Transaction amount
description         (Text) - Human-readable description
balance_before      (Decimal) - Balance before transaction
balance_after       (Decimal) - Balance after transaction
reference_id        (String) - External reference (payment ID, etc.)
notes               (Text) - Additional notes
created_at          (DateTime) - Transaction timestamp
```

## Integration Points

### When to Record Transactions

#### 1. Subscriber Adds Funds
**Where:** `billing/views.py` - `UserBalanceViewSet.add_funds()`

```python
from billing.business_account import record_subscriber_deposit

# After processing payment:
record_subscriber_deposit(
    subscriber=request.user,
    amount=amount,
    reference_id=payment_id,  # From payment gateway
    notes=f'Deposit via {payment_method}'
)
```

#### 2. Subscriber Makes Purchase
**Where:** `market/shop_views.py` - `checkout()` function

```python
from billing.business_account import (
    record_subscriber_purchase,
    record_market_agent_payout
)

# After order is created:
record_subscriber_purchase(
    subscriber=subscriber,
    amount=order_total,
    order=order,
    notes=f'Purchase - {len(items)} items'
)

# Pay market agents:
for item in order.items.all():
    agent_share = item.total_price * 0.9  # 90% to agent
    record_market_agent_payout(
        market_agent=item.product.market_agent,
        amount=agent_share,
        order=order,
        notes=f'{item.product.name} x{item.quantity}'
    )
```

#### 3. Service Agent Gets Paid
**Where:** `orders/views.py` - When order is delivered

```python
from billing.business_account import record_service_agent_payout

# When delivery is complete:
record_service_agent_payout(
    service_agent=delivery_agent,
    amount=delivery_fee,
    order=order,
    notes=f'Delivery completed - Order #{order.id}'
)
```

#### 4. Refunds
**Where:** Any refund process

```python
from billing.business_account import record_refund

# When order is cancelled:
record_refund(
    subscriber=order.subscriber,
    amount=order.total_amount,
    order=order,
    notes='Order cancelled by customer'
)
```

## Generating Financial Reports

Example: Get all admin fees for a date range

```python
from billing.models import BusinessTransaction
from datetime import date

start = date(2026, 1, 1)
end = date(2026, 3, 31)

fees = BusinessTransaction.objects.filter(
    type='admin_fee',
    created_at__date__gte=start,
    created_at__date__lte=end
)

total_fees = sum(t.amount for t in fees)
print(f"Admin fees (Q1 2026): R {total_fees}")
```

## Audit Trail

Every transaction is immutable with:
- **Balance snapshots** (before & after)
- **Timestamps** (when it happened)
- **References** (what order, user, etc.)
- **Notes** (why it happened)

## Best Practices

1. **Always include `order` reference** - Link transactions to orders when applicable
2. **Use meaningful `reference_id`** - Include payment gateway IDs for traceability
3. **Add detailed `notes`** - Help with future audits
4. **Use atomic transactions** - All functions use `@transaction.atomic()` to prevent data loss
5. **Test integration** - Verify transactions are recorded when testing payment flows

## Future Enhancements

- [ ] Daily settlement reports
- [ ] Automated payout scheduling
- [ ] Tax calculation integration
- [ ] Multi-currency support
- [ ] Bank account reconciliation
- [ ] Financial statement generation

## Support

For questions about the business account system, check:
1. `/opt/orderin/billing/business_account.py` - Helper functions
2. `/opt/orderin/billing/models.py` - Database schema
3. `/opt/orderin/billing/serializers.py` - API data format
4. `/opt/orderin/billing/views.py` - API endpoints
