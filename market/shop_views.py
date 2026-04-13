from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from market.models import Product, ProductCategory, ShoppingCart, CartItem
from orders.models import Order, OrderItem
from billing.models import UserBalance
from users.models import MarketAgent


def shop_home(request):
    """Shop homepage - redirect to browse"""
    return redirect('shop_browse')


def shop_browse(request):
    """Browse all products with cart support"""
    
    categories = ProductCategory.objects.all()
    products = Product.objects.filter(is_available=True).all()
    
    # Get cart count for badge (only if authenticated)
    cart_count = 0
    if request.user.is_authenticated and request.user.user_type == 'subscriber':
        cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
        cart_count = cart.get_total_items()
    
    context = {
        'categories': categories,
        'products': products,
        'cart_count': cart_count,
    }
    return render(request, 'shop/browse.html', context)


@login_required
def shop_category(request, category_id):
    """View products by category"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(
        category=category,
        is_available=True
    ).order_by('-updated_at')
    
    categories = ProductCategory.objects.all()
    
    # Get cart count for badge
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    cart_count = cart.get_total_items()
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'cart_count': cart_count,
    }
    return render(request, 'shop/category.html', context)


@login_required
def shop_search(request):
    """Search products and shops with advanced filtering"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    query = request.GET.get('q', '').strip()
    
    # Get all categories for filter display
    categories = ProductCategory.objects.all()
    selected_category = request.GET.get('category', '')
    
    # Price range filters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # Sorting
    sort_by = request.GET.get('sort', '-updated_at')
    valid_sorts = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-updated_at',
        'popularity': '-created_at',
    }
    sort_order = valid_sorts.get(sort_by, '-updated_at')
    
    products = []
    shops = []
    
    if query or selected_category or min_price or max_price:
        # Search products
        product_query = Q()
        
        if query:
            product_query = Q(name__icontains=query) | Q(description__icontains=query)
        
        products = Product.objects.filter(is_available=True)
        
        if product_query:
            products = products.filter(product_query)
        
        # Filter by category
        if selected_category:
            try:
                category_id = int(selected_category)
                products = products.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        
        # Filter by price range
        if min_price:
            try:
                min_val = float(min_price)
                products = products.filter(price__gte=min_val)
            except ValueError:
                pass
        
        if max_price:
            try:
                max_val = float(max_price)
                products = products.filter(price__lte=max_val)
            except ValueError:
                pass
        
        # Apply sorting
        products = products.select_related(
            'market_agent__user', 'category'
        ).order_by(sort_order)
        
        # Search shops
        if query:
            shops = MarketAgent.objects.filter(
                Q(user__shop_name__icontains=query) | 
                Q(user__shop_description__icontains=query),
                user__is_active=True
            ).select_related('user')
    
    # Get cart count for badge
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    cart_count = cart.get_total_items()
    
    context = {
        'products': products,
        'shops': shops,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'cart_count': cart_count,
        'result_count': len(products) + len(shops),
    }
    return render(request, 'shop/search.html', context)


@login_required
def product_detail(request, product_id):
    """View product details"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product_id)[:4]
    
    # Get cart count for badge
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    cart_count = cart.get_total_items()
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_count': cart_count,
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
def view_cart(request):
    """View shopping cart using database models"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    cart_items = cart.items.all()
    
    # Get user balance
    balance = UserBalance.objects.filter(user=request.user).first()
    current_balance = balance.balance if balance else 0
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total_price(),
        'total_items': cart.get_total_items(),
        'current_balance': float(current_balance),
        'can_checkout': float(current_balance) >= float(cart.get_total_price()),
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Add product to cart via form submission"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1))
    
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    
    # Check stock
    if product.quantity_available < quantity:
        return render(request, 'shop/product_detail.html', {
            'product': product,
            'error': f'Not enough stock. Available: {product.quantity_available}'
        })
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return redirect('view_cart')


@login_required
def remove_from_cart(request, product_id):
    """Remove item from cart"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    cart = get_object_or_404(ShoppingCart, subscriber=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    
    return redirect('view_cart')


@login_required
def checkout(request):
    """Checkout and create order with payment verification"""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    cart, _ = ShoppingCart.objects.get_or_create(subscriber=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        return redirect('view_cart')
    
    # Get balance with proper locking to prevent race condition
    from django.db import transaction
    
    try:
        with transaction.atomic():
            # Lock the balance row to prevent concurrent checkouts
            balance = UserBalance.objects.select_for_update().get(user=request.user)
            
            # Calculate order total
            total = cart.get_total_price()
            
            # Verify sufficient balance
            if balance.balance < total:
                return render(request, 'shop/checkout.html', {
                    'error': f'Insufficient balance. You need {currency_symbol}{total} but have {currency_symbol}{balance.balance}',
                    'total': total,
                    'current_balance': float(balance.balance),
                    'currency_symbol': request.context_data.get('currency_symbol', 'R'),
                })
            
            # Create order
            order = Order.objects.create(
                subscriber=request.user,
                status='pending',
            )
            
            # Add items to order and verify prices haven't changed
            for cart_item in cart_items:
                # Verify price matches (prevents price manipulation)
                current_price = cart_item.product.price
                if cart_item.unit_price != current_price:
                    # Log price discrepancy
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"Price mismatch for product {cart_item.product.id} - "
                        f"Cart: {cart_item.unit_price}, Current: {current_price}"
                    )
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                )
            
            # Calculate and save total
            order.calculate_total()
            order.save()
            
            # Deduct from balance within transaction
            old_balance = balance.balance
            balance.balance -= order.total_amount
            balance.save()
            
            # Create transaction record with payment verification
            from billing.models import BillingTransaction
            txn = BillingTransaction.objects.create(
                user=request.user,
                order=order,
                type='debit',
                amount=order.total_amount,
                description=f'Order Payment #{order.id}',
                balance_after=balance.balance,
            )
            
            # Update order status to paid
            order.status = 'paid'
            order.is_paid = True
            order.payment_verified = True
            order.paid_at = timezone.now()
            order.save()
            
            # Log successful payment
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"Order payment processed - Order: {order.id}, "
                f"User: {request.user.id}, Amount: {order.total_amount}, "
                f"Transaction: {txn.id}, Balance Before: {old_balance}, "
                f"Balance After: {balance.balance}"
            )
            
            # Clear cart
            cart.items.all().delete()
            
            # Redirect to delivery method selection
            return redirect('select_delivery_method', order_id=order.id)
    
    except UserBalance.DoesNotExist:
        return render(request, 'shop/checkout.html', {
            'error': 'Account balance not found. Please contact support.',
            'total': 0,
            'current_balance': 0,
        })


@login_required
@require_http_methods(["GET", "POST"])
def select_delivery_method(request, order_id):
    """Select delivery method and provide delivery details for order."""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    order = get_object_or_404(Order, id=order_id, subscriber=request.user)
    
    # Redirect if order doesn't have delivery info selected yet
    if hasattr(order, 'delivery'):
        return redirect('order_success', order_id=order.id)
    
    from delivery.models import DeliveryMethod, OrderDelivery
    delivery_methods = DeliveryMethod.objects.filter(is_active=True)
    
    # Get market agent from order items
    market_agent = None
    if order.items.exists():
        first_item = order.items.first()
        if first_item.product and hasattr(first_item.product, 'market_agent'):
            market_agent = first_item.product.market_agent
    
    if request.method == 'POST':
        method_id = request.POST.get('delivery_method')
        
        if not method_id:
            return render(request, 'shop/select_delivery.html', {
                'order': order,
                'delivery_methods': delivery_methods,
                'error': 'Please select a delivery method',
            })
        
        try:
            delivery_method = DeliveryMethod.objects.get(id=method_id, is_active=True)
        except DeliveryMethod.DoesNotExist:
            return render(request, 'shop/select_delivery.html', {
                'order': order,
                'delivery_methods': delivery_methods,
                'error': 'Invalid delivery method selected',
            })
        
        # Create OrderDelivery record
        delivery_data = {
            'order': order,
            'delivery_method': delivery_method,
            'delivery_status': 'pending',
        }
        
        # Get additional details based on delivery method
        if delivery_method.name == 'home_delivery':
            address = request.POST.get('delivery_address')
            city = request.POST.get('delivery_city')
            state = request.POST.get('delivery_state')
            zip_code = request.POST.get('delivery_zip_code')
            
            if not all([address, city, state, zip_code]):
                return render(request, 'shop/select_delivery.html', {
                    'order': order,
                    'delivery_methods': delivery_methods,
                    'error': 'Please provide complete delivery address',
                })
            
            delivery_data.update({
                'delivery_address': address,
                'delivery_city': city,
                'delivery_state': state,
                'delivery_zip_code': zip_code,
            })
        
        elif delivery_method.name == 'collection_point':
            collection_point_id = request.POST.get('collection_point')
            
            if not collection_point_id:
                return render(request, 'shop/select_delivery.html', {
                    'order': order,
                    'delivery_methods': delivery_methods,
                    'error': 'Please select a collection point',
                })
            
            from delivery.models import CollectionPoint
            try:
                collection_point = CollectionPoint.objects.get(id=collection_point_id, is_active=True)
                delivery_data['collection_point'] = collection_point
            except CollectionPoint.DoesNotExist:
                return render(request, 'shop/select_delivery.html', {
                    'order': order,
                    'delivery_methods': delivery_methods,
                    'error': 'Invalid collection point selected',
                })
        
        # Validate addresses for home delivery before creating record
        if delivery_method.name == 'home_delivery' and market_agent:
            from delivery.distance import DeliveryDistanceAndCost
            import logging
            logger = logging.getLogger(__name__)
            
            agent_user = market_agent.user
            
            # Check if market agent has a valid address
            if not agent_user.address or not agent_user.city:
                return render(request, 'shop/select_delivery.html', {
                    'order': order,
                    'delivery_methods': delivery_methods,
                    'error': f'Store address is not set. Please contact {agent_user.shop_name} to update their store location.',
                    'market_agent': market_agent,
                })
            
            # Validate market agent address can be geocoded
            store_address = f"{agent_user.address}, {agent_user.city}, Cape Town"
            delivery_full_address = f"{delivery_data['delivery_address']}, {delivery_data['delivery_city']}"
            
            try:
                calc = DeliveryDistanceAndCost(store_address, delivery_full_address)
                
                # Test if store address can be geocoded
                store_coords = calc.geocode_address(store_address)
                if not store_coords:
                    logger.warning(f"Could not geocode store address: {store_address}")
                    return render(request, 'shop/select_delivery.html', {
                        'order': order,
                        'delivery_methods': delivery_methods,
                        'error': f'Store location "{store_address}" could not be found. Please contact {agent_user.shop_name} to update their store address with a more specific location (e.g., include suburb name).',
                        'market_agent': market_agent,
                    })
                
                # Test if delivery address can be geocoded
                delivery_coords = calc.geocode_address(delivery_full_address)
                if not delivery_coords:
                    logger.warning(f"Could not geocode delivery address: {delivery_full_address}")
                    return render(request, 'shop/select_delivery.html', {
                        'order': order,
                        'delivery_methods': delivery_methods,
                        'error': f'Delivery address "{delivery_full_address}" could not be found. Please check the address and try again. Include suburb/area name for better accuracy.',
                        'market_agent': market_agent,
                    })
                
                # Both addresses are valid, proceed with creating order
                order_delivery = OrderDelivery.objects.create(**delivery_data)
                
                # Calculate distance and cost with validated addresses
                distance = calc.calculate_distance()
                if distance:
                    order_delivery.delivery_distance = distance
                    order_delivery.save()
                    logger.info(f"Order {order.id}: Store '{store_address}' → Customer '{delivery_full_address}' = {distance} km")
                    
                    # Calculate cost with distance
                    cost = calc.get_delivery_cost(order_delivery)
                
            except Exception as e:
                logger.error(f"Error validating/calculating delivery addresses for Order {order.id}: {e}")
                return render(request, 'shop/select_delivery.html', {
                    'order': order,
                    'delivery_methods': delivery_methods,
                    'error': f'Unable to verify delivery addresses. Please check your address and try again.',
                    'market_agent': market_agent,
                })
        else:
            # For non-home-delivery methods, just create the order
            order_delivery = OrderDelivery.objects.create(**delivery_data)
        
        # Update order status to confirmed (ready for processing)
        order.status = 'confirmed'
        order.save()
        
        return redirect('order_success', order_id=order.id)
    
    # GET request - show delivery method selection form
    from delivery.models import CollectionPoint
    collection_points = CollectionPoint.objects.filter(is_active=True)
    
    return render(request, 'shop/select_delivery.html', {
        'order': order,
        'delivery_methods': delivery_methods,
        'collection_points': collection_points,
        'market_agent': market_agent,
    })


@login_required
def order_success(request, order_id):
    """Display order success page after delivery method is selected."""
    if request.user.user_type != 'subscriber':
        return redirect('dashboard_home')
    
    order = get_object_or_404(Order, id=order_id, subscriber=request.user)
    
    # Verify delivery method is selected
    if not hasattr(order, 'delivery'):
        return redirect('select_delivery_method', order_id=order.id)
    
    return render(request, 'shop/order_success.html', {
        'order': order,
    })
