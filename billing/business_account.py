"""
Business Account Transaction Management

This module handles all transaction routing through the central business account.
All money flows through this account for easy reconciliation and accounting.
"""

from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from .models import BusinessAccount, BusinessTransaction


def get_or_create_business_account():
    """Get or create the main business account."""
    account, created = BusinessAccount.objects.get_or_create(
        name='Order In Business Account',
        defaults={
            'status': 'active',
            'description': 'Central business account for all transactions',
            'total_balance': 0
        }
    )
    return account


def record_subscriber_deposit(subscriber, amount, reference_id=None, notes=None):
    """
    Record when a subscriber deposits money (adds funds).
    Money comes IN to the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        # Lock the account for update
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance += Decimal(str(amount))
        account.save()
        
        # Create transaction record
        BusinessTransaction.objects.create(
            business_account=account,
            subscriber=subscriber,
            type='subscriber_deposit',
            amount=Decimal(str(amount)),
            description=f'Subscriber {subscriber.username} deposited funds',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_subscriber_purchase(subscriber, amount, order=None, reference_id=None, notes=None):
    """
    Record when a subscriber makes a purchase.
    Money goes OUT from the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance -= Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            subscriber=subscriber,
            order=order,
            type='subscriber_purchase',
            amount=Decimal(str(amount)),
            description=f'Subscriber {subscriber.username} purchased from marketplace',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_market_agent_payout(market_agent, amount, order=None, reference_id=None, notes=None):
    """
    Record payment to a market agent.
    Money goes OUT from the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance -= Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            market_agent=market_agent,
            order=order,
            type='market_agent_payout',
            amount=Decimal(str(amount)),
            description=f'Payout to market agent {market_agent.user.username}',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_service_agent_payout(service_agent, amount, order=None, reference_id=None, notes=None):
    """
    Record payment to a service agent.
    Money goes OUT from the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance -= Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            service_agent=service_agent,
            order=order,
            type='service_agent_payout',
            amount=Decimal(str(amount)),
            description=f'Payout to service agent {service_agent.user.username}',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_refund(subscriber, amount, order=None, reference_id=None, notes=None):
    """
    Record a refund to a subscriber.
    Money goes OUT from the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance -= Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            subscriber=subscriber,
            order=order,
            type='refund',
            amount=Decimal(str(amount)),
            description=f'Refund issued to {subscriber.username}',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_admin_fee(amount, description='Admin fee collected', order=None, reference_id=None, notes=None):
    """
    Record admin fees collected (commission from transactions).
    Money comes IN to the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance += Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            order=order,
            type='admin_fee',
            amount=Decimal(str(amount)),
            description=description,
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def record_adjustment(amount, description, reference_id=None, notes=None):
    """
    Record manual adjustments to the business account.
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        account.total_balance += Decimal(str(amount))
        account.save()
        
        BusinessTransaction.objects.create(
            business_account=account,
            type='adjustment',
            amount=Decimal(str(amount)),
            description=description,
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes=notes
        )
    
    return account.total_balance


def get_business_account_balance():
    """Get the current business account balance."""
    account = get_or_create_business_account()
    return account.total_balance


def get_business_transactions(limit=100, offset=0):
    """Get recent business account transactions."""
    return BusinessTransaction.objects.all()[offset:offset+limit]


def get_business_transactions_by_type(transaction_type, limit=100):
    """Get transactions filtered by type."""
    return BusinessTransaction.objects.filter(type=transaction_type)[:limit]


def get_business_transactions_by_date(start_date, end_date):
    """Get transactions within a date range."""
    return BusinessTransaction.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )


def approve_payout_request(payout_request, amount=None):
    """
    Approve a payout request and record the transaction in the business account.
    
    Args:
        payout_request: PayoutRequest instance
        amount: Optional approved amount (defaults to requested amount)
    
    Returns:
        BusinessTransaction instance for the payout
    """
    from django.utils import timezone
    from .models import PayoutRequest, BusinessTransaction
    
    if payout_request.status != 'pending':
        raise ValueError(f"Cannot approve {payout_request.status} payout request")
    
    # Use requested amount if no approved amount specified
    payout_amount = amount or payout_request.amount_requested
    
    with db_transaction.atomic():
        # Lock the business account
        account = BusinessAccount.objects.select_for_update().get(pk=1)
        
        # Update payout request
        payout_request.amount_approved = Decimal(str(payout_amount))
        payout_request.status = 'approved'
        payout_request.approved_at = timezone.now()
        
        # Determine which agent
        agent = payout_request.agent if payout_request.agent else payout_request.service_agent
        
        # Record the payout in business account
        balance_before = account.total_balance
        account.total_balance -= Decimal(str(payout_amount))
        account.save()
        
        transaction = BusinessTransaction.objects.create(
            business_account=account,
            market_agent=payout_request.agent if payout_request.agent_type == 'market' else None,
            service_agent=payout_request.service_agent if payout_request.agent_type == 'service' else None,
            type='market_agent_payout' if payout_request.agent_type == 'market' else 'service_agent_payout',
            amount=Decimal(str(payout_amount)),
            description=f'Payout approved for {agent.user.username}',
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=f'PAYOUT_REQ_{payout_request.id}',
            notes=f'Payout request ID: {payout_request.id}'
        )
        
        # Link the transaction back to the payout request
        payout_request.business_transaction = transaction
        payout_request.save()
    
    return transaction


def get_admin_fee_config():
    """Get the current admin fee configuration."""
    from .models import AdminFeeConfig
    config = AdminFeeConfig.objects.filter(is_active=True).first()
    if not config:
        # Create default (percentage-based)
        config = AdminFeeConfig.objects.create(
            fee_type='percentage',
            percentage=Decimal('5')  # Default 5%
        )
    return config


def calculate_admin_fee(amount):
    """
    Calculate the admin fee based on current configuration.
    
    Args:
        amount: The order amount
    
    Returns:
        Decimal: The admin fee amount
    """
    config = get_admin_fee_config()
    
    if config.fee_type == 'percentage':
        fee = Decimal(str(amount)) * (config.percentage / Decimal('100'))
        return fee.quantize(Decimal('0.01'))
    
    return Decimal('0')


def record_admin_fee(amount, description='Admin fee from sale', reference_id=None):
    """
    Record an admin fee collection in the business account.
    This is called when a subscriber makes a purchase.
    
    Args:
        amount: The fee amount to collect
        description: Description of the fee
        reference_id: Optional reference (order ID, etc.)
    
    Returns:
        BusinessTransaction: The fee transaction record
    """
    account = get_or_create_business_account()
    
    with db_transaction.atomic():
        account = BusinessAccount.objects.select_for_update().get(pk=account.pk)
        
        balance_before = account.total_balance
        fee_amount = Decimal(str(amount))
        account.total_balance += fee_amount
        account.save()
        
        transaction = BusinessTransaction.objects.create(
            business_account=account,
            type='admin_fee',
            amount=fee_amount,
            description=description,
            balance_before=balance_before,
            balance_after=account.total_balance,
            reference_id=reference_id,
            notes='Admin fee collected from sale'
        )
    
    return transaction
