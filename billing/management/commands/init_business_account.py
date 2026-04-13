from django.core.management.base import BaseCommand
from billing.business_account import get_or_create_business_account


class Command(BaseCommand):
    help = 'Initialize the central business account for transaction tracking'

    def handle(self, *args, **options):
        account = get_or_create_business_account()
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Business account initialized: {account.name}\n'
                f'  Status: {account.status}\n'
                f'  Balance: R {account.total_balance}\n'
                f'  ID: {account.id}'
            )
        )
