from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json

from users.models import CustomUser, ServiceAgent, MarketAgent
from market.models import Product
from orders.models import Order, OrderItem
from billing.models import UserBalance, BillingTransaction
from agents.models import ServicePrice


@login_required
def user_profile(request):
    """User profile page"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    # Add user-type specific info
    if user.user_type == 'market_agent':
        market_agent = MarketAgent.objects.filter(user=user).first()
        if market_agent:
            context['market_agent'] = market_agent
            context['total_products'] = market_agent.products.count()
    elif user.user_type == 'subscriber':
        balance = UserBalance.objects.filter(user=user).first()
        if balance:
            context['balance'] = round(balance.balance, 2)
        context['total_orders'] = Order.objects.filter(subscriber=user).count()
    elif user.user_type in ['caterer', 'delivery_person']:
        service_agent = ServiceAgent.objects.filter(user=user).first()
        if service_agent:
            context['service_agent'] = service_agent
    
    return render(request, 'dashboards/user_profile.html', context)


@login_required
def dashboard_home(request):
    """Route to appropriate dashboard based on user type"""
    user_type = request.user.user_type
    
    if user_type == 'admin':
        return redirect('admin_dashboard')
    elif user_type == 'subscriber':
        return redirect('subscriber_dashboard')
    elif user_type == 'market_agent':
        return redirect('market_agent_dashboard')
    elif user_type in ['caterer', 'delivery_person']:
        return redirect('service_agent_dashboard')
    else:
        return redirect('admin_dashboard')


@login_required
def admin_dashboard(request):
    """Admin dashboard with overview metrics"""
    if request.user.user_type != 'admin':
        return redirect('dashboard_home')
    
    # User statistics
    total_users = CustomUser.objects.count()
    subscribers = CustomUser.objects.filter(user_type='subscriber').count()
    market_agents = CustomUser.objects.filter(user_type='market_agent').count()
    service_agents = CustomUser.objects.filter(user_type__in=['caterer', 'delivery_person']).count()
    
    # Order statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='delivered').count()
    
    # Revenue statistics
    total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_revenue = Order.objects.filter(
        status='delivered',
        created_at__date=timezone.now().date()
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Average order value
    avg_order_value = Order.objects.filter(status='delivered').aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    
    # Get last 7 days of order data for chart
    last_7_days = []
    daily_revenue = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        last_7_days.append(date.strftime('%m-%d'))
        
        revenue = Order.objects.filter(
            status='delivered',
            created_at__date=date.date()
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        daily_revenue.append(float(revenue) if revenue else 0)
    
    # Get user type distribution
    user_distribution = {
        'subscribers': subscribers,
        'market_agents': market_agents,
        'service_agents': service_agents,
    }
    
    # Get order status distribution
    pending = Order.objects.filter(status='pending').count()
    processing = Order.objects.filter(status='processing').count()
    delivered = Order.objects.filter(status='delivered').count()
    cancelled = Order.objects.filter(status='cancelled').count()
    
    order_status = {
        'pending': pending,
        'processing': processing,
        'delivered': delivered,
        'cancelled': cancelled,
    }
    
    context = {
        'total_users': total_users,
        'subscribers': subscribers,
        'market_agents': market_agents,
        'service_agents': service_agents,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': round(total_revenue, 2),
        'today_revenue': round(today_revenue, 2),
        'avg_order_value': round(avg_order_value, 2),
        'last_7_days': json.dumps(last_7_days),
        'daily_revenue': json.dumps(daily_revenue),
        'user_distribution': user_distribution,
        'order_status': order_status,
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def subscriber_dashboard(request):
    """Subscriber dashboard with their orders and balance"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    user = request.user
    
    # Get user balance
    balance = UserBalance.objects.filter(user=user).first()
    current_balance = balance.balance if balance else 0
    
    # Get user's orders
    total_orders = Order.objects.filter(subscriber=user).count()
    completed_orders = Order.objects.filter(subscriber=user, status='delivered').count()
    pending_orders = Order.objects.filter(subscriber=user, status__in=['pending', 'processing']).count()
    
    # Total spent
    total_spent = Order.objects.filter(subscriber=user, status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Get recent orders
    recent_orders = Order.objects.filter(subscriber=user).order_by('-created_at')[:5]
    
    # Get spending by category (last 30 days)
    last_30_days = timezone.now() - timedelta(days=30)
    orders_30days = Order.objects.filter(
        subscriber=user,
        status='delivered',
        created_at__gte=last_30_days
    ).prefetch_related('items__product__category')
    
    category_spending = {}
    for order in orders_30days:
        for item in order.items.all():
            category = item.product.category.name
            amount = item.quantity * item.unit_price
            category_spending[category] = category_spending.get(category, 0) + amount
    
    # Prepare chart data
    categories = list(category_spending.keys())
    spending = [float(val) for val in category_spending.values()]  # Convert Decimal to float
    
    # Get transaction history (last 10)
    transactions = BillingTransaction.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get total products available for shopping
    total_products = Product.objects.filter(is_available=True).count()
    
    # Import SiteSettings for currency
    from dashboards.models import SiteSettings
    
    context = {
        'current_balance': round(current_balance, 2),
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_spent': round(total_spent, 2),
        'recent_orders': recent_orders,
        'transactions': transactions,
        'categories': json.dumps(categories),
        'spending': json.dumps(spending),
        'total_products': total_products,
        'currency_symbol': SiteSettings.get_currency(),
    }
    
    return render(request, 'dashboards/subscriber_dashboard.html', context)


@login_required
def market_agent_dashboard(request):
    """Market agent dashboard with their products and sales"""
    if request.user.user_type != 'market_agent':
        return redirect('dashboard_home')
    
    user = request.user
    market_agent = MarketAgent.objects.filter(user=user).first()
    
    if not market_agent:
        return redirect('dashboard_home')
    
    # Product statistics
    total_products = Product.objects.filter(market_agent=market_agent).count()
    available_products = Product.objects.filter(market_agent=market_agent, is_available=True).count()
    low_stock = Product.objects.filter(market_agent=market_agent, quantity_available__lt=10).count()
    
    # Sales statistics
    products = Product.objects.filter(market_agent=market_agent)
    product_ids = products.values_list('id', flat=True)
    
    total_sold = OrderItem.objects.filter(
        product_id__in=product_ids,
        order__status='delivered'
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    total_revenue = OrderItem.objects.filter(
        product_id__in=product_ids,
        order__status='delivered'
    ).aggregate(
        revenue=Sum('quantity') * Sum('unit_price')
    ).get('revenue', 0) or 0
    
    # Better calculation for revenue
    order_items = OrderItem.objects.filter(
        product_id__in=product_ids,
        order__status='delivered'
    )
    total_revenue = sum(item.quantity * item.unit_price for item in order_items)
    
    # Get top products
    top_products = OrderItem.objects.filter(
        product_id__in=product_ids,
        order__status='delivered'
    ).values('product__name').annotate(
        quantity=Sum('quantity')
    ).order_by('-quantity')[:5]
    
    # Get sales by day (last 7 days)
    last_7_days = []
    daily_sales = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        last_7_days.append(date.strftime('%m-%d'))
        
        sales = OrderItem.objects.filter(
            product_id__in=product_ids,
            order__status='delivered',
            order__created_at__date=date.date()
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        daily_sales.append(int(sales) if sales else 0)
    
    # Get products with stock levels
    all_products = products.values('id', 'name', 'quantity_available', 'price').order_by('-quantity_available')
    
    product_names = [p['name'] for p in all_products]
    stock_levels = [p['quantity_available'] for p in all_products]
    
    context = {
        'total_products': total_products,
        'available_products': available_products,
        'low_stock': low_stock,
        'total_sold': int(total_sold),
        'total_revenue': round(total_revenue, 2),
        'top_products': top_products,
        'products': all_products,
        'last_7_days': json.dumps(last_7_days),
        'daily_sales': json.dumps(daily_sales),
        'product_names': json.dumps(product_names),
        'stock_levels': json.dumps(stock_levels),
    }
    
    return render(request, 'dashboards/market_agent_dashboard.html', context)


@login_required
def service_agent_dashboard(request):
    """Service agent dashboard (caterer/delivery person)"""
    if request.user.user_type not in ['caterer', 'delivery_person']:
        return redirect('dashboard_home')
    
    user = request.user
    service_agent = ServiceAgent.objects.filter(user=user).first()
    
    if not service_agent:
        return redirect('dashboard_home')
    
    # Service statistics
    total_bookings = service_agent.orders.count()
    completed_bookings = service_agent.orders.filter(order__status='delivered').count()
    pending_bookings = service_agent.orders.filter(order__status__in=['pending', 'processing']).count()
    
    # Revenue
    total_revenue = service_agent.orders.filter(
        order__status='delivered'
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Rating and reviews
    rating = service_agent.rating
    
    # Get last 7 days bookings
    last_7_days = []
    daily_bookings = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        last_7_days.append(date.strftime('%m-%d'))
        
        bookings = service_agent.orders.filter(
            order__created_at__date=date.date()
        ).count()
        daily_bookings.append(int(bookings))
    
    # Recent bookings
    recent_bookings = service_agent.orders.all().order_by('-order__created_at')[:5]
    
    # If delivery person, show delivery-specific dashboard
    if service_agent.service_type == 'delivery':
        return delivery_agent_dashboard(request)
    
    # Otherwise, show generic service agent dashboard
    context = {
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'total_revenue': round(total_revenue, 2),
        'rating': rating,
        'last_7_days': json.dumps(last_7_days),
        'daily_bookings': json.dumps(daily_bookings),
        'recent_bookings': recent_bookings,
        'service_type': service_agent.service_type,
    }
    
    return render(request, 'dashboards/service_agent_dashboard.html', context)


@login_required
def delivery_agent_dashboard(request):
    """
    Delivery agent dashboard showing assigned orders and delivery methods.
    Displays deliveries to complete with tracking information.
    """
    if request.user.user_type != 'delivery_person':
        return redirect('dashboard_home')
    
    user = request.user
    service_agent = ServiceAgent.objects.filter(user=user).first()
    
    if not service_agent:
        return redirect('dashboard_home')
    
    # Get all delivery assignments for this agent
    try:
        from delivery.models import DeliveryAssignment, DeliveryTracking, OrderDelivery
    except ImportError:
        # Models don't exist yet, return empty dashboard
        context = {
            'service_agent': service_agent,
            'total_deliveries': 0,
            'completed_deliveries': 0,
            'in_progress_deliveries': 0,
            'pending_deliveries': 0,
            'total_earnings': 0,
            'rating': service_agent.rating,
            'assigned_deliveries': [],
            'today_deliveries': [],
            'pending_assignments': [],
            'vehicle': getattr(service_agent.user, 'vehicles', None),
            'message': 'Delivery system integration in progress...'
        }
        return render(request, 'dashboards/delivery_agent_dashboard.html', context)
    
    # Delivery statistics
    assignments = DeliveryAssignment.objects.filter(delivery_agent=service_agent)
    
    total_deliveries = assignments.count()
    completed_deliveries = assignments.filter(assignment_status='completed').count()
    in_progress_deliveries = assignments.filter(assignment_status='in_progress').count()
    pending_deliveries = assignments.filter(assignment_status__in=['assigned', 'accepted']).count()
    
    # Earnings from completed deliveries
    total_earnings = assignments.filter(
        assignment_status='completed'
    ).aggregate(Sum('delivery_fee'))['delivery_fee__sum'] or 0
    
    # Get assigned deliveries (pending and accepted)
    assigned_deliveries = assignments.filter(
        assignment_status__in=['assigned', 'accepted']
    ).select_related(
        'order_delivery',
        'assigned_vehicle'
    ).order_by('-assigned_at')
    
    # Get today's deliveries
    today = timezone.now().date()
    today_deliveries = assignments.filter(
        assigned_at__date=today
    ).exclude(
        assignment_status='completed'
    ).select_related(
        'order_delivery',
        'assigned_vehicle',
        'delivery_tracking'
    ).order_by('assigned_at')
    
    # Get in-progress deliveries with tracking
    in_progress = assignments.filter(
        assignment_status='in_progress'
    ).select_related(
        'order_delivery',
        'assigned_vehicle',
        'delivery_tracking'
    ).prefetch_related('delivery_tracking__tracking_events')
    
    # Get assigned vehicles for this agent
    try:
        vehicles = service_agent.vehicles.all() if hasattr(service_agent, 'vehicles') else []
    except:
        vehicles = []
    
    # Get pending assignments (waiting for agent to accept)
    pending_assignments = assignments.filter(
        assignment_status='assigned'
    ).select_related(
        'order_delivery'
    ).order_by('-assigned_at')[:5]
    
    # Get 7-day trend
    last_7_days = []
    daily_deliveries = []
    
    for i in range(6, -1, -1):
        date = timezone.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        last_7_days.append(date.strftime('%m-%d'))
        
        deliveries = assignments.filter(
            completed_at__date=date.date(),
            assignment_status='completed'
        ).count()
        daily_deliveries.append(int(deliveries))
    
    # Calculate completion rate
    completion_rate = 0
    if total_deliveries > 0:
        completion_rate = round((completed_deliveries / total_deliveries) * 100, 1)
    
    # Get monthly deliveries
    first_day_of_month = timezone.now().replace(day=1)
    monthly_deliveries = assignments.filter(
        assignment_status='completed',
        completed_at__gte=first_day_of_month
    ).count()
    
    context = {
        'service_agent': service_agent,
        'total_deliveries': total_deliveries,
        'completed_deliveries': completed_deliveries,
        'in_progress_deliveries': in_progress_deliveries,
        'pending_deliveries': pending_deliveries,
        'total_earnings': round(total_earnings, 2),
        'rating': service_agent.rating,
        'assigned_deliveries': assigned_deliveries,
        'today_deliveries': today_deliveries,
        'in_progress': in_progress,
        'pending_assignments': pending_assignments,
        'vehicles': vehicles,
        'last_7_days': json.dumps(last_7_days),
        'daily_deliveries': json.dumps(daily_deliveries),
        'completion_rate': completion_rate,
        'monthly_deliveries': monthly_deliveries,
        'currency_symbol': '₹',  # or get from SiteSettings
    }
    
    return render(request, 'dashboards/delivery_agent_dashboard.html', context)
