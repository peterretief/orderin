from .models import SiteSettings


def site_settings(request):
    """Add site settings to template context."""
    # Try to get user's preferred currency
    currency_symbol = 'R'
    
    if request.user.is_authenticated:
        # Use user's preference if they have one set
        currency_symbol = request.user.currency_symbol
    else:
        # Fall back to site default
        try:
            settings = SiteSettings.objects.get(pk=1)
            currency_symbol = settings.currency_symbol
        except SiteSettings.DoesNotExist:
            pass
    
    return {
        'currency_symbol': currency_symbol,
    }
