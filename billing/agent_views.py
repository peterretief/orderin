"""
Agent-specific billing views (earnings, payouts, statements).
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json

from .models import BusinessTransaction, PayoutRequest
from users.models import MarketAgent, ServiceAgent


@login_required
def market_agent_statement(request):
    """
    Market agent's earnings and payout statement.
    Shows money in (sales), money out (payouts), and pending requests.
    """
    # Get the user's market agent profile
    try:
        market_agent = request.user.market_agent_profile
    except:
        return redirect('dashboard_home')
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Build query
    transactions = BusinessTransaction.objects.filter(market_agent=market_agent)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            transactions = transactions.filter(created_at__gte=start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            transactions = transactions.filter(created_at__lte=end_dt)
        except:
            pass
    
    transactions = transactions.order_by('-created_at')
    
    # Calculate totals
    # Money IN = subscriber_purchase (they earned this from customers)
    money_in = transactions.filter(
        type='subscriber_purchase'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Money OUT = market_agent_payout (they received this payment)
    money_out = transactions.filter(
        type='market_agent_payout'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pending balance = earned - paid
    pending_balance = money_in - money_out
    
    # Get payout requests
    payout_requests = PayoutRequest.objects.filter(
        agent=market_agent
    ).order_by('-requested_at')
    
    # Summary by status
    pending_requests = payout_requests.filter(status='pending')
    pending_request_amount = pending_requests.aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
    
    approved_requests = payout_requests.filter(status='approved')
    approved_amount = approved_requests.aggregate(Sum('amount_approved'))['amount_approved__sum'] or 0
    
    paid_requests = payout_requests.filter(status='paid')
    paid_amount = paid_requests.aggregate(Sum('amount_approved'))['amount_approved__sum'] or 0
    
    # Available for payout = pending balance - pending requests
    available_for_payout = pending_balance - pending_request_amount
    
    # Prepare transaction display
    transaction_list = []
    for txn in transactions:
        txn_display = {
            'id': txn.id,
            'date': txn.created_at,
            'type': txn.get_type_display(),
            'type_key': txn.type,
            'description': txn.description,
            'amount': float(txn.amount),
            'reference_id': txn.reference_id,
        }
        
        if txn.type == 'subscriber_purchase':
            txn_display['direction'] = 'in'
            txn_display['direction_emoji'] = '➕'
            txn_display['direction_class'] = 'text-success'
        else:
            txn_display['direction'] = 'out'
            txn_display['direction_emoji'] = '➖'
            txn_display['direction_class'] = 'text-danger'
        
        transaction_list.append(txn_display)
    
    context = {
        'agent': market_agent,
        'money_in': float(money_in),
        'money_out': float(money_out),
        'pending_balance': float(pending_balance),
        'available_for_payout': float(available_for_payout),
        'payout_requests': payout_requests,
        'pending_request_amount': float(pending_request_amount),
        'approved_amount': float(approved_amount),
        'paid_amount': float(paid_amount),
        'transactions': transaction_list,
        'start_date': start_date,
        'end_date': end_date,
        'total_transactions': len(transaction_list),
    }
    
    return render(request, 'billing/market_agent_statement.html', context)


@login_required
def service_agent_statement(request):
    """
    Service agent's earnings and payout statement.
    Shows money in (service bookings), money out (payouts), and pending requests.
    """
    # Get the user's service agent profile
    try:
        service_agent = request.user.service_agent_profile
    except:
        return redirect('dashboard_home')
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Build query
    transactions = BusinessTransaction.objects.filter(service_agent=service_agent)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            transactions = transactions.filter(created_at__gte=start_dt)
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            transactions = transactions.filter(created_at__lte=end_dt)
        except:
            pass
    
    transactions = transactions.order_by('-created_at')
    
    # Money IN from service bookings
    money_in = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Money OUT from payouts
    money_out = transactions.filter(
        type='service_agent_payout'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    pending_balance = money_in - money_out
    
    # Payout requests
    payout_requests = PayoutRequest.objects.filter(
        service_agent=service_agent
    ).order_by('-requested_at')
    
    pending_request_amount = payout_requests.filter(
        status='pending'
    ).aggregate(Sum('amount_requested'))['amount_requested__sum'] or 0
    
    available_for_payout = pending_balance - pending_request_amount
    
    context = {
        'agent': service_agent,
        'money_in': float(money_in),
        'money_out': float(money_out),
        'pending_balance': float(pending_balance),
        'available_for_payout': float(available_for_payout),
        'payout_requests': payout_requests,
        'pending_request_amount': float(pending_request_amount),
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'billing/service_agent_statement.html', context)
