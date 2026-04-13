from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django import forms
from django.contrib import messages
from django.db import IntegrityError, transaction
from users.models import CustomUser


class RegistrationForm(forms.Form):
    """Form for user registration."""
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'autofocus': True
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        }),
        required=True,
        help_text='Must be at least 8 characters'
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password'
        }),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Passwords do not match.')
        
        if password and len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        
        username = cleaned_data.get('username')
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken.')
        
        email = cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        
        return cleaned_data


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
    """Home page - landing page with role selection"""
    return render(request, 'home.html')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration view with role selection."""
    user_type = request.GET.get('type', 'subscriber')
    
    # Validate user type
    valid_types = [choice[0] for choice in CustomUser.USER_TYPE_CHOICES if choice[0] != 'admin']
    if user_type not in valid_types:
        return redirect('home')
    
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # Double-check for duplicates before creating (race condition protection)
            if CustomUser.objects.filter(username=username).exists():
                form.add_error('username', f'Username "{username}" is already taken. Please choose another.')
                return render(request, 'auth/register.html', {
                    'form': form,
                    'user_type': user_type,
                    'user_type_display': dict(CustomUser.USER_TYPE_CHOICES).get(user_type, 'User')
                })
            
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', f'Email "{email}" is already registered. Please use another.')
                return render(request, 'auth/register.html', {
                    'form': form,
                    'user_type': user_type,
                    'user_type_display': dict(CustomUser.USER_TYPE_CHOICES).get(user_type, 'User')
                })
            
            try:
                # Use atomic transaction to ensure all-or-nothing creation
                with transaction.atomic():
                    # Triple-check immediately before creation (in transaction)
                    if CustomUser.objects.filter(username=username).exists():
                        raise IntegrityError("Username already exists")
                    if CustomUser.objects.filter(email=email).exists():
                        raise IntegrityError("Email already exists")
                    
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=email,
                        password=form.cleaned_data['password'],
                        user_type=user_type
                    )
                    # Try to create API token (optional, not critical for login)
                    try:
                        from rest_framework.authtoken.models import Token
                        Token.objects.get_or_create(user=user)
                    except Exception:
                        # Token creation is optional, don't fail registration if it fails
                        pass
                
                messages.success(request, f'Account created successfully! Welcome to Order In as a {user_type.replace("_", " ").title()}.')
                login(request, user)
                return redirect('dashboard_home')
            except (IntegrityError, Exception) as e:
                # If IntegrityError occurred, absolutely no user was created
                error_msg = str(e).lower()
                if 'username' in error_msg:
                    error_text = 'Username is already taken. Please choose a different username.'
                elif 'email' in error_msg:
                    error_text = 'Email is already registered. Please use a different email.'
                else:
                    error_text = f'Registration failed: {str(e)}'
                
                messages.error(request, error_text)
                # Re-render form so user can try again
                return render(request, 'auth/register.html', {
                    'form': form,
                    'user_type': user_type,
                    'user_type_display': dict(CustomUser.USER_TYPE_CHOICES).get(user_type, 'User')
                })
        else:
            # Form has validation errors, show them
            return render(request, 'auth/register.html', {
                'form': form,
                'user_type': user_type,
                'user_type_display': dict(CustomUser.USER_TYPE_CHOICES).get(user_type, 'User')
            })
    else:
        form = RegistrationForm()
    
    user_type_display = dict(CustomUser.USER_TYPE_CHOICES).get(user_type, 'User')
    
    return render(request, 'auth/register.html', {
        'form': form,
        'user_type': user_type,
        'user_type_display': user_type_display
    })


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
