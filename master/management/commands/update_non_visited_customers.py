import datetime

from django.db.models import Q
from django.core.management.base import BaseCommand

from client_management.models import DialyCustomers, InactiveCustomers

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        date = datetime.datetime.today().date() - datetime.timedelta(days=1)
        todays_customers = DialyCustomers.objects.filter(is_guest=False, date=date)
        
        for customer in todays_customers:
            inactive_instance,create = InactiveCustomers.objects.get_or_create(
                customer=customer
            )
            
            if customer.is_supply:
                inactive_instance.inactive_days = 0
            else:
                inactive_instance.inactive_days += 1
            inactive_instance.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all customers'))
