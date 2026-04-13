"""
Admin dashboard views for the business account.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import BusinessAccount, BusinessTransaction


@login_required
def business_account_dashboard(request):
    """
    View the business account and all transactions.
    Admin only.
    """
    if not request.user.is_staff:
        return redirect('dashboard_home')
    
    # Get the main business account
    try:
        account = BusinessAccount.objects.get(name='Order In Business Account')
    except BusinessAccount.DoesNotExist:
        context = {'error': 'Business account not initialized'}
        return render(request, 'billing/business_account_dashboard.html', context)
    
    # Get recent transactions
    recent_transactions = BusinessTransaction.objects.all().order_by('-created_at')[:20]
    
    # Get transactions by type summary
    transaction_summary = {}
    for trans_type, trans_label in BusinessTransaction.TRANSACTION_TYPE_CHOICES:
        count = BusinessTransaction.objects.filter(type=trans_type).count()
        total = BusinessTransaction.objects.filter(type=trans_type).aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        transaction_summary[trans_type] = {
            'label': trans_label,
            'count': count,
            'total': float(total)
        }
    
    # Summary statistics
    total_in = sum(
        v['total'] for k, v in transaction_summary.items() 
        if k in ['subscriber_deposit', 'admin_fee']
    )
    total_out = sum(
        v['total'] for k, v in transaction_summary.items() 
        if k in ['subscriber_purchase', 'market_agent_payout', 'service_agent_payout', 'refund']
    )
    
    # Get last 7 days data for chart
    last_7_days = []
    daily_in = []
    daily_out = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        last_7_days.append(date.strftime('%m-%d'))
        
        # Money in
        in_amount = BusinessTransaction.objects.filter(
            type__in=['subscriber_deposit', 'admin_fee'],
            created_at__date=date.date()
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        daily_in.append(float(in_amount))
        
        # Money out
        out_amount = BusinessTransaction.objects.filter(
            type__in=['subscriber_purchase', 'market_agent_payout', 'service_agent_payout', 'refund'],
            created_at__date=date.date()
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        daily_out.append(float(out_amount))
    
    context = {
        'account': account,
        'recent_transactions': recent_transactions,
        'transaction_summary': transaction_summary,
        'total_in': total_in,
        'total_out': total_out,
        'net': account.total_balance,
        'last_7_days': json.dumps(last_7_days),
        'daily_in': json.dumps(daily_in),
        'daily_out': json.dumps(daily_out),
        'total_transactions': BusinessTransaction.objects.count(),
    }
    
    return render(request, 'billing/business_account_dashboard.html', context)


@login_required
def transaction_detail(request, transaction_id):
    """View details of a specific transaction."""
    if not request.user.is_staff:
        return redirect('dashboard_home')
    
    transaction = BusinessTransaction.objects.get(pk=transaction_id)
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'billing/transaction_detail.html', context)


@login_required
def transactions_by_type(request, transaction_type):
    """View all transactions of a specific type."""
    if not request.user.is_staff:
        return redirect('dashboard_home')
    
    # Get the label for this type
    type_label = dict(BusinessTransaction.TRANSACTION_TYPE_CHOICES).get(
        transaction_type, 'Unknown'
    )
    
    transactions = BusinessTransaction.objects.filter(
        type=transaction_type
    ).order_by('-created_at')
    
    # Group by day
    daily_summary = {}
    for trans in transactions:
        date_key = trans.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_summary:
            daily_summary[date_key] = {'count': 0, 'total': 0, 'transactions': []}
        daily_summary[date_key]['count'] += 1
        daily_summary[date_key]['total'] += float(trans.amount)
        daily_summary[date_key]['transactions'].append(trans)
    
    context = {
        'transaction_type': transaction_type,
        'type_label': type_label,
        'transactions': transactions,
        'daily_summary': daily_summary,
        'total_count': transactions.count(),
        'total_amount': sum(float(t.amount) for t in transactions),
    }
    
    return render(request, 'billing/transactions_by_type.html', context)


@login_required
def bank_statement(request):
    """
    Bank statement view with all transactions as money in/out.
    Shows complete transaction history with filtering.
    """
    if not request.user.is_staff:
        return redirect('dashboard_home')
    
    # Get the main business account
    try:
        account = BusinessAccount.objects.get(name='Order In Business Account')
    except BusinessAccount.DoesNotExist:
        context = {'error': 'Business account not initialized'}
        return render(request, 'billing/bank_statement.html', context)
    
    # Start with all transactions
    transactions = BusinessTransaction.objects.all()
    
    # Apply date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_dt = timezone.datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            transactions = transactions.filter(created_at__gte=start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = timezone.datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            transactions = transactions.filter(created_at__lte=end_dt)
        except:
            pass
    
    # Apply transaction type filter
    filter_type = request.GET.get('type')
    if filter_type:
        transactions = transactions.filter(type=filter_type)
    
    # Order by date
    transactions = transactions.order_by('-created_at')
    
    # Calculate totals
    total_in = transactions.filter(
        type__in=['subscriber_deposit', 'admin_fee']
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_out = transactions.filter(
        type__in=['subscriber_purchase', 'market_agent_payout', 'service_agent_payout', 'refund']
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Prepare transactions for display with money in/out designation
    transaction_list = []
    for txn in transactions:
        txn_display = {
            'id': txn.id,
            'date': txn.created_at,
            'type': txn.get_type_display(),
            'type_key': txn.type,
            'description': txn.description,
            'amount': float(txn.amount),
            'balance_after': float(txn.balance_after),
            'reference_id': txn.reference_id,
        }
        
        # Mark as money in or out
        if txn.type in ['subscriber_deposit', 'admin_fee']:
            txn_display['direction'] = 'in'
            txn_display['direction_emoji'] = '➕'
            txn_display['direction_class'] = 'text-success'
        elif txn.type in ['subscriber_purchase', 'market_agent_payout', 'service_agent_payout', 'refund']:
            txn_display['direction'] = 'out'
            txn_display['direction_emoji'] = '➖'
            txn_display['direction_class'] = 'text-danger'
        else:
            txn_display['direction'] = 'adjust'
            txn_display['direction_emoji'] = '🔄'
            txn_display['direction_class'] = 'text-info'
        
        transaction_list.append(txn_display)
    
    context = {
        'account': account,
        'transactions': transaction_list,
        'total_in': float(total_in),
        'total_out': float(total_out),
        'net_change': float(total_in - total_out),
        'current_balance': float(account.total_balance),
        'transaction_types': BusinessTransaction.TRANSACTION_TYPE_CHOICES,
        'start_date': start_date,
        'end_date': end_date,
        'filter_type': filter_type,
        'total_transactions': len(transaction_list),
    }
    
    return render(request, 'billing/bank_statement.html', context)
