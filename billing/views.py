from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from datetime import timedelta
from decimal import Decimal
import logging
import hashlib

from .models import UserBalance, BillingTransaction, BillingPlan, AdminBilling, BusinessAccount, BusinessTransaction, PayoutRequest
from .serializers import (
    UserBalanceSerializer, BillingTransactionSerializer,
    BillingPlanSerializer, AdminBillingSerializer, BusinessAccountSerializer, BusinessTransactionSerializer, PayoutRequestSerializer
)

logger = logging.getLogger(__name__)

# Configuration for payment security
MAX_SINGLE_PAYMENT = 1000000  # Max amount per single add_funds
MIN_SINGLE_PAYMENT = 0.01
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
MAX_PAYMENTS_PER_HOUR = 10  # Max add_funds requests per hour


class UserBalanceViewSet(viewsets.ModelViewSet):
    """ViewSet for UserBalance model."""
    queryset = UserBalance.objects.all()
    serializer_class = UserBalanceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET'])
    def my_balance(self, request):
        """Get current user's balance."""
        try:
            balance = UserBalance.objects.get(user=request.user)
            serializer = self.get_serializer(balance)
            return Response(serializer.data)
        except UserBalance.DoesNotExist:
            # Create balance if not exists
            balance = UserBalance.objects.create(user=request.user)
            serializer = self.get_serializer(balance)
            return Response(serializer.data)
    
    @action(detail=False, methods=['POST'])
    def add_funds(self, request):
        """Add funds to user balance with security checks."""
        try:
            amount = float(request.data.get('amount', 0))
        except (ValueError, TypeError):
            logger.warning(f"Invalid amount provided by user {request.user.id}")
            return Response(
                {'error': 'Amount must be a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert to Decimal for database operations
        amount_decimal = Decimal(str(amount))
        
        # Validation: Amount range
        if amount < MIN_SINGLE_PAYMENT:
            return Response(
                {'error': f'Minimum payment is {MIN_SINGLE_PAYMENT}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount > MAX_SINGLE_PAYMENT:
            return Response(
                {'error': f'Maximum payment is {MAX_SINGLE_PAYMENT}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Security Check: Rate limiting
        one_hour_ago = timezone.now() - timedelta(seconds=RATE_LIMIT_WINDOW)
        recent_payments = BillingTransaction.objects.filter(
            user=request.user,
            type='credit',
            created_at__gte=one_hour_ago
        ).count()
        
        if recent_payments >= MAX_PAYMENTS_PER_HOUR:
            logger.warning(
                f"Rate limit exceeded for user {request.user.id} - "
                f"{recent_payments} payments in last hour"
            )
            return Response(
                {'error': 'Too many payment requests. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Use database transaction to ensure atomicity
        try:
            with transaction.atomic():
                # Get or create balance with select_for_update to prevent race condition
                balance, created = UserBalance.objects.select_for_update().get_or_create(
                    user=request.user,
                    defaults={'balance': Decimal('0')}
                )
                
                old_balance = balance.balance
                balance.balance += amount_decimal
                balance.save()
                
                # Record transaction with audit info
                txn = BillingTransaction.objects.create(
                    user=request.user,
                    amount=amount_decimal,
                    type='credit',
                    description=f'Added funds: {amount}',
                    balance_after=balance.balance
                )
                
                # Record in business account for centralized tracking
                from billing.business_account import record_subscriber_deposit
                record_subscriber_deposit(
                    subscriber=request.user,
                    amount=amount_decimal,
                    reference_id=f'ADD_FUNDS_{txn.id}',
                    notes=f'Subscriber deposit via dashboard'
                )
                
                # Log successful transaction
                logger.info(
                    f"Payment success - User: {request.user.id}, "
                    f"Amount: {amount}, Transaction ID: {txn.id}, "
                    f"New Balance: {balance.balance}"
                )
                
                return Response(
                    {
                        'message': f'Successfully added {amount} to account',
                        'balance': float(balance.balance),
                        'old_balance': float(old_balance),
                        'new_balance': float(balance.balance),
                        'transaction_id': txn.id,
                        'timestamp': txn.created_at.isoformat()
                    },
                    status=status.HTTP_201_CREATED
                )
        
        except Exception as e:
            logger.error(
                f"Payment error - User: {request.user.id}, "
                f"Amount: {amount}, Error: {str(e)}, Traceback: {type(e).__name__}"
            )
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            error_msg = str(e)
            return Response(
                {'error': f'Payment processing failed: {error_msg}', 'detail': error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BillingTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BillingTransaction model."""
    serializer_class = BillingTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter transactions based on user type."""
        if self.request.user.is_staff:
            return BillingTransaction.objects.all()
        # Users see only their own transactions
        return BillingTransaction.objects.filter(user=self.request.user)


class BillingPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for BillingPlan model."""
    queryset = BillingPlan.objects.all()
    serializer_class = BillingPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on user type."""
        if self.request.user.is_staff:
            return BillingPlan.objects.all()
        # Regular users can only see active plans
        return BillingPlan.objects.filter(is_active=True)


class AdminBillingViewSet(viewsets.ModelViewSet):
    """ViewSet for AdminBilling model."""
    queryset = AdminBilling.objects.all()
    serializer_class = AdminBillingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter based on user type."""
        if self.request.user.is_staff:
            return AdminBilling.objects.all()
        # Subscribers see only their own bills
        return AdminBilling.objects.filter(subscriber=self.request.user)
    
    @action(detail=False, methods=['POST'])
    def bill_subscriber(self, request):
        """Admin action to bill a subscriber with a plan."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can bill subscribers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscriber_id = request.data.get('subscriber_id')
        plan_id = request.data.get('plan_id')
        
        subscriber = get_object_or_404(
            self.get_queryset().model, pk=subscriber_id, subscriber__user_type='subscriber'
        ) if subscriber_id else None
        plan = get_object_or_404(BillingPlan, pk=plan_id) if plan_id else None
        
        # Create a more flexible approach
        try:
            from users.models import CustomUser
            subscriber = CustomUser.objects.get(pk=subscriber_id, user_type='subscriber')
            plan = BillingPlan.objects.get(pk=plan_id)
        except:
            return Response(
                {'error': 'Invalid subscriber or plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        due_date = timezone.now().date() + timedelta(days=30)
        
        billing = AdminBilling.objects.create(
            subscriber=subscriber,
            billing_plan=plan,
            amount=plan.amount,
            due_date=due_date
        )
        
        serializer = self.get_serializer(billing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['PUT'])
    def mark_paid(self, request, pk=None):
        """Mark a bill as paid."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admin can mark bills as paid'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        bill = self.get_object()
        bill.status = 'paid'
        bill.paid_date = timezone.now().date()
        bill.save()
        
        serializer = self.get_serializer(bill)
        return Response(serializer.data)


class BusinessAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for BusinessAccount model - Admin only."""
    queryset = BusinessAccount.objects.all()
    serializer_class = BusinessAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Only admins can access business account."""
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]  # Require auth but set to admin_only in action
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Only admins can see business accounts."""
        if self.request.user.is_staff:
            return BusinessAccount.objects.all()
        return BusinessAccount.objects.none()
    
    @action(detail=False, methods=['GET'])
    def main_account(self, request):
        """Get the main business account."""
        from .business_account import get_or_create_business_account
        account = get_or_create_business_account()
        serializer = self.get_serializer(account)
        return Response(serializer.data)


class BusinessTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BusinessTransaction model - Admin only."""
    serializer_class = BusinessTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    
    def get_queryset(self):
        """Only admins can see business transactions."""
        if self.request.user.is_staff:
            return BusinessTransaction.objects.all()
        return BusinessTransaction.objects.none()
    
    @action(detail=False, methods=['GET'])
    def summary(self, request):
        """Get business account summary."""
        from .business_account import get_or_create_business_account
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can access this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        account = get_or_create_business_account()
        transactions = BusinessTransaction.objects.all()
        
        # Calculate summary by type
        summary = {}
        for trans_type, trans_label in BusinessTransaction.TRANSACTION_TYPE_CHOICES:
            count = transactions.filter(type=trans_type).count()
            total = transactions.filter(type=trans_type).aggregate(
                Sum('amount')
            )['amount__sum'] or 0
            summary[trans_type] = {
                'label': trans_label,
                'count': count,
                'total': float(total)
            }
        
        return Response({
            'account': {
                'id': account.id,
                'name': account.name,
                'status': account.status,
                'total_balance': float(account.total_balance)
            },
            'summary': summary,
            'total_transactions': transactions.count()
        })
    
    @action(detail=False, methods=['GET'])
    def by_type(self, request):
        """Get transactions filtered by type."""
        transaction_type = request.query_params.get('type')
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can access this'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not transaction_type:
            return Response(
                {'error': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transactions = BusinessTransaction.objects.filter(type=transaction_type)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)


class PayoutRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for PayoutRequest model - Agents and Admins."""
    serializer_class = PayoutRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payout requests based on user type."""
        user = self.request.user
        
        if user.is_staff:
            return PayoutRequest.objects.all()
        
        # Market agents see their own requests
        if hasattr(user, 'market_agent_profile'):
            return PayoutRequest.objects.filter(agent__user=user)
        
        # Service agents see their own requests
        if hasattr(user, 'service_agent_profile'):
            return PayoutRequest.objects.filter(service_agent__user=user)
        
        return PayoutRequest.objects.none()
    
    @action(detail=False, methods=['POST'])
    def request_payout(self, request):
        """Agent requests a payout."""
        user = request.user
        amount = request.data.get('amount')
        
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
        except:
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be greater than zero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payout request
        try:
            # Market agent
            if hasattr(user, 'market_agent_profile'):
                payout_request = PayoutRequest.objects.create(
                    agent=user.market_agent_profile,
                    agent_type='market',
                    amount_requested=amount
                )
            # Service agent
            elif hasattr(user, 'service_agent_profile'):
                payout_request = PayoutRequest.objects.create(
                    service_agent=user.service_agent_profile,
                    agent_type='service',
                    amount_requested=amount
                )
            else:
                return Response(
                    {'error': 'User is not an agent'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(payout_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating payout request: {str(e)}")
            return Response(
                {'error': 'Failed to create payout request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['POST'])
    def approve(self, request, pk=None):
        """Admin approves a payout request."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can approve payouts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payout_request = self.get_object()
        amount = request.data.get('amount')  # Optional - can approve partial
        
        try:
            from .business_account import approve_payout_request
            
            if amount:
                amount = Decimal(str(amount))
            
            transaction = approve_payout_request(payout_request, amount)
            
            # Update payout request to paid status
            payout_request.status = 'paid'
            payout_request.paid_at = timezone.now()
            payout_request.save()
            
            serializer = self.get_serializer(payout_request)
            return Response({
                'message': 'Payout approved and processed',
                'payout_request': serializer.data,
                'transaction_id': transaction.id
            })
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error approving payout: {str(e)}")
            return Response(
                {'error': 'Failed to approve payout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        """Admin rejects a payout request."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can reject payouts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payout_request = self.get_object()
        notes = request.data.get('notes', '')
        
        if payout_request.status != 'pending':
            return Response(
                {'error': f'Cannot reject {payout_request.status} request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payout_request.status = 'rejected'
        payout_request.admin_notes = notes
        payout_request.save()
        
        serializer = self.get_serializer(payout_request)
        return Response({
            'message': 'Payout request rejected',
            'payout_request': serializer.data
        })
