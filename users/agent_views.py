from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django import forms
from django.contrib import messages
from users.models import MarketAgent


class AgentAddressForm(forms.Form):
    """Form for market agents to edit their store address."""
    address = forms.CharField(
        label='Store Address',
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Street address, building number, etc.'
        }),
        required=True
    )
    city = forms.CharField(
        label='City',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Cape Town'
        }),
        required=True
    )
    state = forms.CharField(
        label='State/Province',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Western Cape'
        }),
        required=False
    )
    zip_code = forms.CharField(
        label='Zip/Postal Code',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 7800'
        }),
        required=False
    )


@login_required
def upload_products(request):
    """Agent product upload page."""
    if request.user.user_type != 'market_agent':
        return redirect('home')
    
    context = {}
    return render(request, 'agent/upload_products.html', context)


@login_required
def my_products(request):
    """View market agent's own products."""
    if request.user.user_type != 'market_agent':
        return redirect('home')
    
    market_agent = MarketAgent.objects.filter(user=request.user).first()
    products = market_agent.products.all() if market_agent else []
    
    context = {
        'products': products,
        'market_agent': market_agent,
    }
    return render(request, 'agent/my_products.html', context)


@login_required
def agent_dashboard(request):
    """Market agent dashboard with sales, products, and earnings."""
    if request.user.user_type != 'market_agent':
        return redirect('home')
    
    market_agent = MarketAgent.objects.filter(user=request.user).first()
    
    if market_agent:
        products = market_agent.products.all()
        total_products = products.count()
        total_stock = sum(p.quantity_available for p in products)
        
        # Calculate sales statistics
        from orders.models import OrderItem
        sales_items = OrderItem.objects.filter(product__market_agent=market_agent)
        total_sales = sum(item.total_price for item in sales_items)
        total_items_sold = sum(item.quantity for item in sales_items)
    else:
        products = []
        total_products = 0
        total_stock = 0
        total_sales = 0
        total_items_sold = 0
    
    context = {
        'market_agent': market_agent,
        'products': products,
        'total_products': total_products,
        'total_stock': total_stock,
        'total_sales': total_sales,
        'total_items_sold': total_items_sold,
    }
    return render(request, 'agent/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_agent_address(request):
    """Edit market agent's store address."""
    if request.user.user_type != 'market_agent':
        return redirect('home')
    
    market_agent = get_object_or_404(MarketAgent, user=request.user)
    
    if request.method == 'POST':
        form = AgentAddressForm(request.POST)
        if form.is_valid():
            # Update the user's address information
            request.user.address = form.cleaned_data['address']
            request.user.city = form.cleaned_data['city']
            request.user.state = form.cleaned_data['state']
            request.user.zip_code = form.cleaned_data['zip_code']
            request.user.save()
            
            messages.success(request, 'Your store address has been updated successfully!')
            return redirect('agent_dashboard')
    else:
        # Pre-populate form with current address
        form = AgentAddressForm(initial={
            'address': request.user.address or '',
            'city': request.user.city or '',
            'state': request.user.state or '',
            'zip_code': request.user.zip_code or '',
        })
    
    context = {
        'form': form,
        'market_agent': market_agent,
        'page_title': f'Edit Store Address - {market_agent.user.shop_name}',
    }
    return render(request, 'agent/edit_address.html', context)
