from django.db import models


class SiteSettings(models.Model):
    """Global site settings."""
    currency_symbol = models.CharField(max_length=10, default='R', help_text='Currency symbol (e.g., $, €, R)')
    currency_name = models.CharField(max_length=50, default='Rand', help_text='Full currency name')
    
    class Meta:
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return f'Site Settings - {self.currency_symbol}'
    
    @classmethod
    def get_currency(cls):
        """Get the current currency symbol."""
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings.currency_symbol
    
    @classmethod
    def get_currency_name(cls):
        """Get the current currency name."""
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings.currency_name
