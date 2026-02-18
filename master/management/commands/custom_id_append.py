from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Customers

class Command(BaseCommand):
    help = 'Add custom ID for each customer based on created date'

    def handle(self, *args, **kwargs):
        customers = Customers.objects.order_by('created_date')

        custom_id_counter = 1

        for customer in customers:
            custom_id = f"{custom_id_counter:04d}"
            customer.custom_id = custom_id
            customer.save()

            custom_id_counter += 1

        self.stdout.write(self.style.SUCCESS('Custom IDs added successfully for all customers.'))


