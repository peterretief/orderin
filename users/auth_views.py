from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django import forms
from django.contrib import messages
from rest_framework.authtoken.models import Token


class UserProfileForm(forms.Form):
    """Form for editing user profile information."""
    first_name = forms.CharField(
        label='First Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your first name'
        }),
        required=False
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your last name'
        }),
        required=False
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        required=True
    )
    phone = forms.CharField(
        label='Phone Number',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+27 123 456 7890'
        }),
        required=False
    )
    address = forms.CharField(
        label='Street Address',
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Street address, building number, etc.'
        }),
        required=False
    )
    city = forms.CharField(
        label='City/Town',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Cape Town'
        }),
        required=False
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
        label='Postal Code',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 7800'
        }),
        required=False
    )
    # Banking Information Fields
    bank_name = forms.CharField(
        label='Bank Name',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Standard Bank, FNB, Investec'
        }),
        required=False
    )
    bank_account_holder_name = forms.CharField(
        label='Account Holder Full Name',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name as it appears in the bank'
        }),
        required=False
    )
    bank_account_number = forms.CharField(
        label='Account Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank account number'
        }),
        required=False
    )
    bank_branch_code = forms.CharField(
        label='Branch Code',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 051001'
        }),
        required=False
    )
    bank_account_type = forms.ChoiceField(
        label='Account Type',
        choices=[
            ('', 'Select account type...'),
            ('savings', 'Savings Account'),
            ('checking', 'Cheque Account'),
            ('business', 'Business Account'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False
    )
    # Business Information Fields (for market agents and service providers)
    shop_name = forms.CharField(
        label='Business Name',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Fresh Produce Market, Organic Farm'
        }),
        required=False
    )
    shop_description = forms.CharField(
        label='Business Description',
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Describe your business, products, and services'
        }),
        required=False
    )

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Web login page"""
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            return render(request, 'auth/login.html', {
                'error': 'Invalid username or password',
                'username': username
            })
    
    return render(request, 'auth/login.html')


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """Logout view - POST only for security"""
    logout(request)
    return redirect('login')


def home_view(request):
    """Home page - redirects to login or dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    return redirect('login')


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Edit user profile - phone, email, address, location, banking information, and business details"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Update user name information
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            # Update contact information
            request.user.email = form.cleaned_data['email']
            request.user.phone = form.cleaned_data['phone']
            # Update location information
            request.user.address = form.cleaned_data['address']
            request.user.city = form.cleaned_data['city']
            request.user.state = form.cleaned_data['state']
            request.user.zip_code = form.cleaned_data['zip_code']
            # Update banking information
            request.user.bank_name = form.cleaned_data['bank_name']
            request.user.bank_account_holder_name = form.cleaned_data['bank_account_holder_name']
            request.user.bank_account_number = form.cleaned_data['bank_account_number']
            request.user.bank_branch_code = form.cleaned_data['bank_branch_code']
            request.user.bank_account_type = form.cleaned_data['bank_account_type']
            # Update business information (for market agents)
            request.user.shop_name = form.cleaned_data['shop_name']
            request.user.shop_description = form.cleaned_data['shop_description']
            request.user.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('edit_profile')
    else:
        # Pre-populate form with current user data
        form = UserProfileForm(initial={
            'first_name': request.user.first_name or '',
            'last_name': request.user.last_name or '',
            'email': request.user.email,
            'phone': request.user.phone or '',
            'address': request.user.address or '',
            'city': request.user.city or '',
            'state': request.user.state or '',
            'zip_code': request.user.zip_code or '',
            'bank_name': request.user.bank_name or '',
            'bank_account_holder_name': request.user.bank_account_holder_name or '',
            'bank_account_number': request.user.bank_account_number or '',
            'bank_branch_code': request.user.bank_branch_code or '',
            'bank_account_type': request.user.bank_account_type or '',
            'shop_name': request.user.shop_name or '',
            'shop_description': request.user.shop_description or '',
        })
    
    # Determine user type display name
    user_type_display = {
        'subscriber': 'Subscriber',
        'market_agent': 'Market Agent',
        'delivery_person': 'Delivery Person',
        'caterer': 'Caterer',
        'admin': 'Administrator',
    }
    
    context = {
        'form': form,
        'user_type': user_type_display.get(request.user.user_type, request.user.user_type),
        'page_title': 'Edit Profile',
        'is_market_agent': request.user.user_type == 'market_agent',
    }
    return render(request, 'auth/edit_profile.html', context)
