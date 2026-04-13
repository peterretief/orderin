from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser, MarketAgent, ServiceAgent
from market.models import Product, ProductCategory
from orders.models import Order, OrderItem
from billing.models import UserBalance, BillingTransaction


@login_required
@require_http_methods(["GET"])
def admin_users_management(request):
    """Admin page to manage users"""
    if request.user.user_type != 'admin':
        return redirect('dashboard_home')
    
    # Get filter parameters
    user_type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Get all users
    users = CustomUser.objects.all()
    
    # Apply type filter
    if user_type_filter != 'all':
        users = users.filter(user_type=user_type_filter)
    
    # Apply search
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Add user-specific stats
    users_with_stats = []
    for user in users.order_by('-created_at')[:100]:
        stats = {'user': user}
        
        if user.user_type == 'subscriber':
            balance = UserBalance.objects.filter(user=user).first()
            orders = Order.objects.filter(subscriber=user).count()
            stats['balance'] = balance.balance if balance else 0
            stats['orders'] = orders
        elif user.user_type == 'market_agent':
            agent = MarketAgent.objects.filter(user=user).first()
            if agent:
                stats['products'] = agent.products.count()
                stats['shop_name'] = user.shop_name
        
        users_with_stats.append(stats)
    
    context = {
        'users': users_with_stats,
        'user_types': CustomUser.USER_TYPE_CHOICES,
        'selected_type': user_type_filter,
        'search': search_query,
        'status': status_filter,
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'dashboards/admin_users.html', context)


@login_required
@require_http_methods(["GET"])
def admin_products_management(request):
    """Admin page to manage products"""
    if request.user.user_type != 'admin':
        return redirect('dashboard_home')
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    agent_filter = request.GET.get('agent', '')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Get all products
    products = Product.objects.all()
    
    # Apply category filter
    if category_filter:
        try:
            category_id = int(category_filter)
            products = products.filter(category_id=category_id)
        except (ValueError, TypeError):
            pass
    
    # Apply agent filter
    if agent_filter:
        try:
            agent_id = int(agent_filter)
            products = products.filter(market_agent_id=agent_id)
        except (ValueError, TypeError):
            pass
    
    # Apply search
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply availability filter
    if status_filter == 'available':
        products = products.filter(is_available=True)
    elif status_filter == 'unavailable':
        products = products.filter(is_available=False)
    elif status_filter == 'low_stock':
        products = products.filter(quantity_available__lt=5)
    
    # Get related data for filters
    categories = ProductCategory.objects.all()
    agents = MarketAgent.objects.all()
    
    context = {
        'products': products.order_by('-created_at')[:100],
        'categories': categories,
        'agents': agents,
        'selected_category': category_filter,
        'selected_agent': agent_filter,
        'search': search_query,
        'status': status_filter,
        'total_products': Product.objects.count(),
        'available_products': Product.objects.filter(is_available=True).count(),
        'low_stock': Product.objects.filter(quantity_available__lt=5).count(),
    }
    
    return render(request, 'dashboards/admin_products.html', context)


@login_required
@require_http_methods(["GET"])
def admin_orders_management(request):
    """Admin page to manage orders"""
    if request.user.user_type != 'admin':
        return redirect('dashboard_home')
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    agent_filter = request.GET.get('agent', '')
    
    # Get all orders
    orders = Order.objects.all().select_related('subscriber')
    
    # Apply status filter
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Apply search
    if search_query:
        orders = orders.filter(
            Q(subscriber__username__icontains=search_query) |
            Q(subscriber__email__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Get status choices
    status_choices = Order.STATUS_CHOICES
    
    # Summary statistics
    today = timezone.now().date()
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='delivered'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    context = {
        'orders': orders.order_by('-created_at')[:100],
        'statuses': status_choices,
        'selected_status': status_filter,
        'search': search_query,
        'total_orders': Order.objects.count(),
        'today_orders': today_orders,
        'today_revenue': float(today_revenue),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'paid_orders': Order.objects.filter(status='paid').count(),
    }
    
    return render(request, 'dashboards/admin_orders.html', context)


@login_required
@require_http_methods(["GET"])
def admin_analytics(request):
    """Admin analytics and reporting"""
    if request.user.user_type != 'admin':
        return redirect('dashboard_home')
    
    # Time range filter
    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Revenue analytics
    revenue_data = Order.objects.filter(
        status='delivered',
        created_at__gte=start_date
    ).aggregate(
        total=Sum('total_amount'),
        avg=Avg('total_amount'),
        count=Count('id')
    )
    
    # User growth
    new_users = CustomUser.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Top products
    top_products = Product.objects.filter(
        orderitem__order__status='delivered',
        orderitem__order__created_at__gte=start_date
    ).annotate(
        total_sold=Count('id'),
        total_revenue=Sum('orderitem__total_price')
    ).order_by('-total_revenue')[:10]
    
    # Top agents
    top_agents = MarketAgent.objects.annotate(
        total_products=Count('products')
    ).order_by('-total_products')[:10]
    
    context = {
        'days': days,
        'revenue': revenue_data.get('total', 0),
        'avg_order': revenue_data.get('avg', 0),
        'orders': revenue_data.get('count', 0),
        'new_users': new_users,
        'top_products': top_products,
        'top_agents': top_agents,
    }
    
    return render(request, 'dashboards/admin_analytics.html', context)
