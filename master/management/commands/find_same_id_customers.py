from django.core.management.base import BaseCommand
from django.db.models import Count
from accounts.models import Customers

class Command(BaseCommand):
    help = 'Find customers with duplicate custom IDs'

    def handle(self, *args, **kwargs):
        # Find duplicate custom_ids
        duplicates = Customers.objects.values('custom_id') \
            .annotate(id_count=Count('customer_id')) \
            .filter(id_count__gt=1)

        if duplicates.exists():
            self.stdout.write(self.style.WARNING('Duplicate custom IDs found:'))
            
            for dup in duplicates:
                # Fetch customers with the duplicate custom_id
                duplicate_customers = Customers.objects.filter(is_guest=False, custom_id=dup['custom_id'])
                
                self.stdout.write(f"Custom ID: {dup['custom_id']}")
                
                for customer in duplicate_customers:
                    self.stdout.write(f"  - Customer ID: {customer.customer_id}, Name: {customer.customer_name}, Created Date: {customer.created_date}")
        else:
            self.stdout.write(self.style.SUCCESS('No duplicate custom IDs found.'))
