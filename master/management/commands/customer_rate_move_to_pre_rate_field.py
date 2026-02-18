import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import Customers

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        Instances = Customers.objects.filter(is_guest=False, rate__in=["6.5"])
        
        for customer in Instances:
            
            # if customer.rate != None:
            #     rate = Decimal(customer.rate)
            # else:
            #     rate = 0
                
            # customer.prevous_rate = rate
            # customer.save()
            
            self.stdout.write(self.style.WARNING(f'Successfully updated {customer.customer_name} -- {customer.rate} -- {customer.prevous_rate}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
