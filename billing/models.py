from django.db import models
from users.models import CustomUser
from orders.models import Order


class UserBalance(models.Model):
    """User account balance for prepaid orders."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} - Balance: {self.balance}'


class BillingTransaction(models.Model):
    """Record of all billing transactions."""
    
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit (Add Funds)'),
        ('debit', 'Debit (Order Charge)'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='billing_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_transactions')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField()
    
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_type_display()} {self.amount}'


class BillingPlan(models.Model):
    """Billing plans for admin billing to subscribers."""
    
    PLAN_TYPE_CHOICES = (
        ('monthly', 'Monthly Subscription'),
        ('per_order', 'Per Order'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Amount charged')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.name} ({self.get_plan_type_display()})'


class AdminBilling(models.Model):
    """Record of admin billing to subscribers."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_billings')
    billing_plan = models.ForeignKey(BillingPlan, on_delete=models.PROTECT)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    billing_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-billing_date']
    
    def __str__(self):
        return f'{self.subscriber.username} - {self.billing_plan.name} ({self.status})'


class BusinessAccount(models.Model):
    """
    Central business account that holds all transaction records.
    All money flows through this account for easy reconciliation.
    """
    
    ACCOUNT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    name = models.CharField(max_length=255, default='Order In Business Account', unique=True)
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, null=True)
    
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                       help_text='Total balance in business account')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - Balance: {self.total_balance}'


class BusinessTransaction(models.Model):
    """
    All business transactions routed through the central business account.
    Tracks money in and out with full traceability.
    """
    
    TRANSACTION_TYPE_CHOICES = (
        ('subscriber_deposit', 'Subscriber Deposit (Money In)'),          # Subscribers add funds
        ('subscriber_purchase', 'Subscriber Purchase (Money Out)'),        # Subscribers buy from market agents
        ('market_agent_payout', 'Market Agent Payout (Money Out)'),        # Market agents get paid
        ('service_agent_payout', 'Service Agent Payout (Money Out)'),      # Service agents get paid
        ('refund', 'Refund (Money Out)'),                                  # Customer refunds
        ('admin_fee', 'Admin Fee (Money In)'),                             # Commission/fee collected
        ('adjustment', 'Adjustment'),                                      # Manual adjustments
    )
    
    business_account = models.ForeignKey(BusinessAccount, on_delete=models.CASCADE, 
                                        related_name='transactions')
    
    # Links to relevant entities
    subscriber = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='business_transactions_as_subscriber')
    market_agent = models.ForeignKey('users.MarketAgent', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='business_transactions_as_market_agent')
    service_agent = models.ForeignKey('users.ServiceAgent', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='business_transactions_as_service_agent')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='business_transactions')
    
    # Transaction details
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    
    # Balance tracking
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Metadata
    reference_id = models.CharField(max_length=255, blank=True, null=True, 
                                    help_text='External reference (payment gateway ID, order ID, etc.)')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.amount} - {self.created_at.strftime("%Y-%m-%d")}'


class PayoutRequest(models.Model):
    """
    Market/Service agent payout requests.
    Agents request payment, admin approves and payment is processed.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    )
    
    AGENT_TYPE_CHOICES = (
        ('market', 'Market Agent'),
        ('service', 'Service Agent'),
    )
    
    # Agent info
    agent = models.ForeignKey('users.MarketAgent', on_delete=models.CASCADE, 
                             related_name='payout_requests_market', null=True, blank=True)
    service_agent = models.ForeignKey('users.ServiceAgent', on_delete=models.CASCADE, 
                                     related_name='payout_requests_service', null=True, blank=True)
    agent_type = models.CharField(max_length=10, choices=AGENT_TYPE_CHOICES)
    
    # Request details
    amount_requested = models.DecimalField(max_digits=12, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True, null=True)
    
    # Business transaction reference
    business_transaction = models.ForeignKey(BusinessTransaction, on_delete=models.SET_NULL, 
                                            null=True, blank=True, related_name='payout_request')
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        agent_name = self.agent.user.username if self.agent else self.service_agent.user.username
        return f'Payout Request - {agent_name} - {self.amount_requested} - {self.status.upper()}'


class AdminFeeConfig(models.Model):
    """
    Configuration for how admin fees are calculated.
    Can be either:
    - Fixed amount per month
    - Percentage of sales
    """
    
    FEE_TYPE_CHOICES = (
        ('fixed', 'Fixed Monthly Amount'),
        ('percentage', 'Percentage of Sales'),
    )
    
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='percentage')
    
    # If fee_type is 'fixed': Amount to charge per month
    fixed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                      help_text='Monthly fixed fee amount (e.g., 500.00 Rand)')
    
    # If fee_type is 'percentage': Percentage to take from each sale
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0,
                                    help_text='Percentage of sales (e.g., 5 for 5%)')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Admin Fee Config'
    
    def __str__(self):
        if self.fee_type == 'fixed':
            return f'Admin Fee: R {self.fixed_amount} per month'
        else:
            return f'Admin Fee: {self.percentage}% of sales'
